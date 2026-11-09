import sys, ezdxf, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
src,out,x0,x1,y0,y1=sys.argv[1],sys.argv[2],*map(float,sys.argv[3:7])
layers=set(sys.argv[7].split('|')) if len(sys.argv)>7 and sys.argv[7] else None
doc=ezdxf.readfile(src)
fig=plt.figure(figsize=(16,16*(y1-y0)/(x1-x0)),dpi=100); ax=fig.add_axes([0,0,1,1])
ctx=RenderContext(doc)
ctx.set_current_layout(doc.modelspace())
fe=Frontend(ctx,MatplotlibBackend(ax))
ents=[e for e in doc.modelspace() if (layers is None or e.dxf.layer in layers)]
fe.draw_entities(ents) if hasattr(fe,'draw_entities') else fe.draw_layout(doc.modelspace())
pass
ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.grid(True,lw=.3,alpha=.5)
fig.set_size_inches(16,16*(y1-y0)/(x1-x0)); ax.set_position([0,0,1,1]); fig.savefig(out,dpi=100); print('ok',out)
