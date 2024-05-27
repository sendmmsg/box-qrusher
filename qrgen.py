#!/usr/bin/env python3
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
import qrcode.image.svg
import io

def get_qr_svg(text):
    factory = qrcode.image.svg.SvgPathImage
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        image_factory=factory,
        box_size=10,
        border=1,
        version=2
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(back_color="white")
    svg_file = io.BytesIO()
    img.save(svg_file)
    res = svg_file.getbuffer().tobytes().decode()
    return res

def render_svg(prefix,pagenum):
    from bs4 import BeautifulSoup
    paths = []
    labels = []
    xnum = 4
    ynum = 4
    xoff = 6
    yoff = 0
    xwidth = 50
    ywidth = 60
    for y in range(ynum):
        for x in range(xnum):
            c = x + y*xnum + pagenum*(xnum*ynum)
            b = BeautifulSoup(get_qr_svg(f"{prefix}{c}"), features="lxml")
            tag = b.path
            tag["id"] = f"qr-tag-{c}"
            tag["transform"] = f"translate({xoff+x*xwidth} {yoff+y*ywidth})"
            paths.append(str(tag))
            label = f'<text x="{20 + x*xwidth}" y="{46+y*ywidth}" class="small" font-family="Ubuntu" >{c}</text>'
            labels.append(label)

    strio = io.StringIO()
    res = ""
    res += "<?xml version='1.0' encoding='UTF-8'?>"
    res += f'<svg width="210mm" height="297mm" version="1.1" viewBox="0 0 {xnum*50} {ynum*50}" xmlns="http://www.w3.org/2000/svg">'
    for path in paths:
        res += path
    for label in labels:
        res += label

    res += "</svg>"
    return res

with open("page0.svg", "w+") as fp:
    fp.write(render_svg("http://frasse.fenrir-turtle.ts.net/q/",0))
with open("page1.svg", "w+") as fp:
    fp.write(render_svg("http://frasse.fenrir-turtle.ts.net/q/",1))
with open("page2.svg", "w+") as fp:
    fp.write(render_svg("http://frasse.fenrir-turtle.ts.net/q/",2))
