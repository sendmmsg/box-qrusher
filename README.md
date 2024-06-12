# Box QRusher 3000

***Django application for labeling boxes, tagging their contents, and photographing their insides.***

QRusher is a simple Django application that allows you to self-host an index of whatever containers you want to keep track off.
1. Lets you generate SVGs with QR tags that can be printed (on e.g. adhesive paper), and attached to whatever containers you have. 
2. The QR code can then be scanned, and content added/removed from the box, and photos captured and associated with it.
3. The Django app should be reachable from the global internet, easily achivable with e.g. [Tailscale Funnel](https://tailscale.com/kb/1311/tailscale-funnel).
4. QR codes are numbered, both in their content as well as visually, this allows you to find your stuff in the database even if you lack an internet connect, QR code scanner, etc. 

Setting up an externally reachable address at e.g. `https://t.f-r.ts.net/` and feeding that into the QR code generator would generate tags pointing at `https//t.f-r.ts.net/q/0`, `https//t.f-r.ts.net/q/1`, and so on. Generated tags will also have their number printed next to them. 

