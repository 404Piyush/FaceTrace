"""Streamlit UI: Search -> Anchor -> Verify (3 buttons, 60s demo)."""
import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

import blockchain
import search as search_mod
from face_id import find_best

load_dotenv()

st.set_page_config(page_title="Face -> Web -> Chain Verify", layout="wide")
st.title("Face Identification + Blockchain Verification")

query_file = st.file_uploader("1. Upload face scan (input.jpg)", type=["jpg", "jpeg", "png"])
public_url = st.text_input("Public URL of query image (upload to catbox.moe first, Lens needs a URL)")
api_key = st.text_input("SerpAPI key (or set SERPAPI_KEY in .env)", type="password")

if query_file:
    Path("input.jpg").write_bytes(query_file.getvalue())
    st.image("input.jpg", caption="Query face", width=240)

if st.button("Search web for matching post"):
    with st.spinner("Calling SerpAPI Google Lens..."):
        try:
            cands = search_mod.lens_search(public_url, api_key or None)
            st.session_state["raw_response"] = True
        except Exception as e:
            st.warning(f"Live search failed ({e}), using cached candidates.json")
            cands = search_mod.load_cached()
        locals_ = search_mod.download_candidates(cands)
        result = find_best("input.jpg", locals_)
        st.session_state["cands"] = cands
        st.session_state["locals"] = locals_
        st.session_state["result"] = result

if "result" in st.session_state:
    result = st.session_state["result"]
    cands = st.session_state.get("cands", [])
    best = result.get("best")
    if best:
        idx = st.session_state.get("locals", []).index(best["path"]) if best["path"] in st.session_state.get("locals", []) else 0
        post = cands[idx] if idx < len(cands) else {"link": "", "title": ""}
        c1, c2 = st.columns(2)
        c1.image("input.jpg", caption="Query")
        c2.image(best["path"], caption=f"Match: {post.get('title','')}")
        st.write(f"verified={best['verified']} distance={best['distance']:.3f} threshold={best['threshold']:.2f}")
        st.markdown(f"**Source post:** {post.get('link','')}")
        with st.expander("SerpAPI matches JSON (genuineness proof)"):
            st.json(cands)
        st.session_state["post"] = post
        st.session_state["best_path"] = best["path"]

if "post" in st.session_state:
    post = st.session_state["post"]
    post_url = st.text_input("Post URL to anchor", value=post.get("link", ""))
    snippet = st.text_input("Post snippet (edit to demo tamper FAIL)", value=post.get("title", ""))
    if st.button("Anchor on-chain"):
        record = {
            "post_url": post_url,
            "image_sha256": blockchain.image_sha256(st.session_state["best_path"]),
            "text": snippet,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }
        fp = blockchain.fingerprint(record)
        att = blockchain.anchor(fp)
        st.session_state["record"] = record
        st.session_state["fp"] = fp
        st.session_state["att"] = att
        st.success(f"Anchored: tx={att['tx_hash']} block={att['block']} fp={fp[:16]}...")
    if "att" in st.session_state and st.button("Re-verify"):
        cur = dict(st.session_state["record"])
        cur["post_url"] = post_url
        cur["text"] = snippet
        cur_fp = blockchain.fingerprint(cur)
        ok = blockchain.verify(cur_fp, st.session_state["att"]["tx_hash"])
        st.success(f"MATCH block #{st.session_state['att']['block']}") if ok else st.error("FAIL: TAMPER DETECTED")
        st.code(json.dumps({"expected_fp": st.session_state["fp"], "recomputed_fp": cur_fp}, indent=2))
