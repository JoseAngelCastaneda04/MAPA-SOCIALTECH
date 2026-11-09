import sys, ezdxf, matplotlib, yaml, numpy as np, cv2
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
dxf,yml,out,layers=sys.argv[1],sys.argv[2],sys.argv[3],set(sys.argv[4].split('|'))
x0,x1,y0,y1=map(float,sys.argv[5:9])
y=yaml.safe_load(open(yml)); import os
img=cv2.imread(os.path.join(os.path.dirname(yml),y['image']),0); res=y['resolution']; ox,oy=y['origin'][:2]
H,W=img.shape; ext=[ox,ox+W*res,oy,oy+H*res]
doc=ezdxf.readfile(dxf)
fig=plt.figure(figsize=(16,16*(y1-y0)/(x1-x0))); ax=fig.add_axes([0,0,1,1]); ax.set_facecolor('white')
ctx=RenderContext(doc); ctx.set_current_layout(doc.modelspace())
fe=Frontend(ctx,MatplotlibBackend(ax)); fe.draw_entities([e for e in doc.modelspace() if e.dxf.layer in layers])
rgba=np.zeros((H,W,4)); rgba[img==0]=(1,0,0,0.45)
ax.imshow(rgba,extent=ext,origin='upper',zorder=5)
ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.grid(True,lw=.3,alpha=.4)
fig.set_size_inches(16,16*(y1-y0)/(x1-x0)); ax.set_position([0,0,1,1]); fig.savefig(out,dpi=100); print('ok')
