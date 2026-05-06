    # 多模型分析
    print(f"\n🤖 开始用 {len(ANALYSIS_MODELS)} 个模型并发分析 {len(to_analyze)} 篇论文...\n")
    papers_data = []
    for i, paper in enumerate(to_analyze, 1):
        print(f"[{i}/{len(to_analyze)}] 分析: {paper['title'][:60]}...")
        models_results, merged = analyze_paper_multi_model(paper, ANALYSIS_MODELS)
        papers_data.append({
            "paper": paper,
            "merged": merged,
            "models_results": models_results
        })

    # 标记已分析
    for p in to_analyze:
        seen_ids.add(p["id"])
    save_seen_ids(seen_ids)

    # 生成多模型报告
    print("\n📝 生成多模型报告...")
    generate_markdown_multi(papers_data, keywords)