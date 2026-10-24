import plotly.express as px
import streamlit as st
from engine import validation_metrics
from ui.components import kpi
from ui.i18n import t

def render() -> None:
    st.title(t("trust_title"))
    metrics = validation_metrics(); st.caption(metrics.get("provenance", "Evaluation dataset unavailable"))
    cols = st.columns(4)
    for col, name, value in zip(cols,["Precision","Recall","F1","Accuracy"],[metrics["precision"],metrics["recall"],metrics["f1"],metrics["accuracy"]]):
        with col: kpi(name, f"{value:.0%}")
    fig = px.imshow(metrics["matrix"], text_auto=True, x=["Safe predicted","Risk predicted"], y=["Safe actual","Risk actual"], color_continuous_scale=[[0,"#071420"],[1,"#8B5CF6"]], title="Confusion matrix")
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.subheader(t("how_safe"))
    for item in ["Never renders pages", "Manual redirect tracing with a hop limit", "Private-IP blocking", "Size and time caps", "No cookies and no JavaScript execution"]: st.markdown(f"✅ {item}")
    st.subheader(t("limitations"))
    for item in ["Reduces risk; it does not guarantee safety.", "New domains may be unseen.", "No JavaScript-rendered content is evaluated."]: st.markdown(f"• {item}")
    st.subheader(t("roadmap"))
    st.markdown('<div class="steps"><div class="step-card">Browser extension</div><div class="step-card">Slack / Teams bot</div><div class="step-card">REST API</div><div class="step-card">Mobile app</div></div>', unsafe_allow_html=True)
    # TODO: replace prototype evaluation with a labelled production validation set in Phase 2.

if __name__ == "__main__": render()
