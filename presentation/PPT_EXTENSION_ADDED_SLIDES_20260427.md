# DSCI441 Presentation Extension — Extra Slides

This file provides **three extra slides** for the existing 15-slide deck in:

- `presentation/DSCI441_Used_Car_Price_Prediction_Presentation.pdf`

The goal is to insert the upgraded content without rewriting the original deck.

---

## Slide A

**Insert after current Slide 13: `Error Distribution Analysis`**

Suggested slide title:

- `Advanced Diagnostics: Error Is Not Uniform Across the Market`

Suggested on-slide message:

- Global RMSE is useful, but it hides where the model struggles.
- Error grows quickly in the expensive tail.
- Error also changes across vehicle-age and condition groups.
- These plots move the project from score reporting to segment-aware analysis.

Suggested images:

- `results/advanced/bias_by_price_decile_hgb_ordinal.png`
- `results/advanced/error_by_age_bucket_hgb_ordinal.png`
- `results/advanced/mae_by_condition_hgb_ordinal.png`

Suggested layout:

- Left: `bias_by_price_decile_hgb_ordinal.png` as the main wide figure
- Right top: `error_by_age_bucket_hgb_ordinal.png`
- Right bottom: `mae_by_condition_hgb_ordinal.png`
- Bottom text box: short interpretation bullets

### One-minute speech

English:

This slide answers a simple question: does the model make the same kind of error for every car? The answer is no. The price-decile plot shows that the model is much more stable in lower and middle price ranges, but the error grows sharply for expensive listings. The top decile reaches about ten thousand dollars in MAE, so a single global RMSE is not enough to describe the whole system.

The age-bucket and condition-based plots point in the same direction. The model is not equally reliable across all segments, and some groups are clearly easier to predict than others. This part is important because it turns the project from a single-score comparison into a more realistic analysis of where the model is strong and where more caution is needed.

中文：

在这一页新增内容里，我想回答一个很直接的问题：这个模型对所有车辆的误差是不是都差不多？我的答案是否定的。价格分位图说明，模型在低价和中间价格区间相对更稳定，但在高价挂牌中误差会明显增大。最高价格分位的 MAE 大约达到一万美元左右，所以只看一个全局 RMSE 是不够的。

我还放入了按车龄和车况划分的图。这些图说明模型在不同分组上的可靠性并不一样，有些群体明显更容易预测，有些则更难。这部分很重要，因为它让这个项目从单纯比一个分数，变成了更贴近真实应用场景的分析，也让我能更清楚地说明模型哪里强、哪里要谨慎解释。

---

## Slide B

**Insert after current Slide 14: `Feature Importance and Interpretation`**

Suggested slide title:

- `Deployment-Facing Diagnostics: Calibration and Hard Segments`

Suggested on-slide message:

- Calibration-style and interaction diagnostics extend the original evaluation story.
- The decile calibration plot checks whether predicted means track true means across the market.
- The condition x fuel heatmap reveals hard market intersections.
- The key conclusion is not that the model is bad; the key conclusion is that confidence should depend on segment.

Suggested images:

- `results/advanced/calibration_pred_vs_true_decile_hgb_ordinal.png`
- `results/advanced/mae_heatmap_condition_fuel_hgb_ordinal.png`
- `results/advanced/mae_by_fuel_hgb_ordinal.png`

Suggested layout:

- Left: `calibration_pred_vs_true_decile_hgb_ordinal.png`
- Right: `mae_heatmap_condition_fuel_hgb_ordinal.png`
- Bottom narrow strip: `mae_by_fuel_hgb_ordinal.png`
- Side bullets: deployment interpretation

### One-minute speech

English:

This slide explains the upgraded diagnostics from a deployment point of view. The decile calibration plot is useful because it shows whether mean predictions stay aligned with mean true prices across the market. In these results, the alignment is still fairly good overall, but the extremes are more fragile. That means the model captures the broad structure, but it should not use the same confidence language for every price band.

The heatmap and fuel-based error plots tell a similar story in another form. Some condition and fuel combinations are clearly harder than others. So the conclusion is not that the model fails. The conclusion is that the model needs segment-aware interpretation. If I present this model to a user, I should show the prediction together with a warning about which parts of the market are naturally less stable.

中文：

这一页主要是从部署和使用角度来解释这些升级后的诊断图。价格分位校准图的作用，是检查在不同价格区间里，预测均值和真实均值是不是还能保持一致。从结果来看，整体趋势还是对的，但在两端区间会更脆弱一些。这说明模型抓住了市场的大结构，但我不能对所有价格区间都用同样的信心表达。

热力图和按燃料类型的误差图又从另一个角度说明了同样的问题：有些车况和燃料组合明显比其他组合更难预测。所以我的结论不是模型完全失效，而是这个模型需要“分组感知”的解释方式。如果我要把这个系统展示给用户，我应该把预测值和相应的风险提示一起给出来，而不是只给一个数字。

---

## Slide C

**Insert after current Slide 15: `Demo, Limitations, and Conclusion`**

Suggested slide title:

- `GitHub Pages Demo: Static but Shareable`

Suggested on-slide message:

- In addition to the local Streamlit app, I built a GitHub Pages version under `docs/`.
- This web version cannot run live inference, so I use precomputed examples.
- It still shows the project story clearly: problem, model results, advanced diagnostics, and demo flow.
- The static site is useful for sharing, grading, and fast repository review.

Suggested images:

- `presentation/slide_extension_assets/webapp_overview.png`
- `presentation/slide_extension_assets/webapp_results.png`
- Optional small inset: `results/streamlit_demo.png`

Suggested layout:

- Left: webapp overview screenshot
- Right: webapp results screenshot
- Bottom: one short comparison box
  - local Streamlit = runnable demo
  - GitHub Pages = shareable static demo

### One-minute speech

English:

This slide shows the GitHub Pages web app. The site is static, so it does not run live inference the way the Streamlit app does. Instead, it uses precomputed example cases and fixed result pages. The reason is practical. GitHub Pages is easy to share, easy to review, and easy to keep online with the repository.

This is not just a design extra. It changes how the project can be presented. The local Streamlit app still proves that the pipeline is runnable end to end. The GitHub Pages version makes the same project easier to browse, especially for people who want to see the main results and diagnostics quickly. Together, these two demos make the final package more complete.

中文：

这一页展示的是 GitHub Pages 版本的网站。这个版本是静态的，所以它不像 Streamlit 那样能够做实时推理，而是通过预先计算好的示例和固定的结果页面来展示项目。这样做的原因很实际：GitHub Pages 更容易分享，也更方便别人快速查看。

对我来说，这不只是一个外观补充，而是改变了这个项目的展示方式。本地 Streamlit 继续证明整个推理流程是可以跑通的，而 GitHub Pages 版本则让同一个项目更容易被浏览，尤其适合想快速了解结果和诊断分析的人。所以这两个 Demo 放在一起，会让整个最终交付更完整。
