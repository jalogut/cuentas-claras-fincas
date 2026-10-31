from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import re, shutil, zipfile, textwrap, json, base64

OUT=Path('/mnt/data/Cuentas_Claras_Fiel_al_Mockup')
if OUT.exists(): shutil.rmtree(OUT)
(OUT/'assets/backups').mkdir(parents=True)
reference=Image.open('/mnt/data/a_clean_modern_website_design_mockup_collage_with.png').convert('RGB')

def photo(filename,rect,target=(1200,750)):
    image=reference.crop(rect)
    # upscale rather than display tiny mockup crops at their source size
    image=image.resize(target,Image.Resampling.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.0,percent=85,threshold=3))
    image.save(OUT/'assets'/filename,quality=90,subsampling=0,optimize=True)

photo('residencial-hero.jpg',(248,55,506,246),(1120,900))
photo('aerotermia-jardin.jpg',(16,371,248,528),(1100,740))
photo('aerotermia-servicios.jpg',(833,532,995,658),(1000,720))
photo('aerotermia-cabecera.jpg',(798,56,1011,200),(1200,810))
photo('edificio-contacto.jpg',(1304,538,1512,659),(1200,760))
photo('edificio-detalle.jpg',(1330,58,1520,132),(1200,500))

# Take the user's building/check icon from the high resolution original logo, remove navy backing.
original=Image.open('/mnt/data/1792312253283.jpg').convert('RGB')
# Full original 2048 wide, content logo from x320 to 855, y430 to 935.
source=original.crop((312,416,857,934))
source=source.resize((440,418),Image.Resampling.LANCZOS)
# The source logo's background is dark navy; transparency derived from distance to backing color.
# Background varies slightly through gradient, thus use median of left and right margin for each row.
from PIL import ImageStat
pix=source.load(); W,H=source.size
out=Image.new('RGBA',(W,H)); target=out.load()
for y in range(H):
    # side sample out-of-mark pixels (the left 4px and rightmost 4px)
    c1=source.getpixel((W-2,y));c2=source.getpixel((2,y))
    # original has near-uniform background; take right side, occasionally sampled mark near left
    bg=c1
    for x in range(W):
        r,g,b=pix[x,y]
        dist=((r-bg[0])**2+(g-bg[1])**2+(b-bg[2])**2)**.5
        # keep vibrant green/white; reduce black/navy noise
        greenboost=max(0,g-r*.95) if g>r else 0
        alpha=int(min(255,max(0,(dist-14)*11+greenboost*.5)))
        target[x,y]=(r,g,b,alpha)
box=out.getbbox()
if box:out=out.crop(box)
out.thumbnail((520,520))
out.save(OUT/'assets'/'isotipo-cuentas-claras.webp')

# Brand color / sections from exact mockup.
icons={
 'honestidad':'<path d="M12 3c-4 0-7 3-7 7v3c0 5 7 8 7 8s7-3 7-8v-3c0-4-3-7-7-7Z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
 'eye':'<path d="M2 12s3.8-6.5 10-6.5S22 12 22 12s-3.8 6.5-10 6.5S2 12 2 12Z"/><circle cx="12" cy="12" r="3.4"/>',
 'aero':'<circle cx="12" cy="12" r="2.2"/><path d="M12 9.8C8.5 2.2 15.2 2 17 5c1.7 2.9-1.9 5.2-5 4.8ZM14.2 12C21.8 8.5 22 15.2 19 17c-2.9 1.7-5.2-1.9-4.8-5ZM12 14.2C15.5 21.8 8.8 22 7 19c-1.7-2.9 1.9-5.2 5-4.8ZM9.8 12C2.2 15.5 2 8.8 5 7c2.9-1.7 5.2 1.9 4.8 5Z"/>',
 'calculator':'<rect x="5" y="2.5" width="14" height="19" rx="2"/><path d="M8 7h8M8 11h2m4 0h2M8 15h2m4 0h2M8 19h2m4 0h2"/>',
 'building':'<path d="M4 21V6l8-3 8 3v15M2.5 21h19"/><path d="M8 9h1m6 0h1M8 13h1m6 0h1M8 17h1m6 0h1"/>',
 'bolt':'<path d="m13 2-9 12h7l-1 8 10-13h-7Z"/>',
 'users':'<circle cx="9" cy="8" r="3"/><path d="M3 20v-2c0-3 2.7-4 6-4s6 1 6 4v2M17 5a3 3 0 0 1 0 6m.8 4c2.2.8 3.2 2.3 3.2 5"/>',
 'phone':'<path d="M6.5 3.5h3l2 4.5-2.5 2c1 2.5 3 4.6 5.5 5.6l2-2.6 4.5 2v3c0 1.7-1.4 2.7-3 2.4C10 18.8 5.2 14 3.8 7c-.4-1.6.6-3.5 2.7-3.5Z"/>',
 'mail':'<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="m3 7.5 9 6.5 9-6.5"/>',
 'pin':'<path d="M12 22s7.5-7.3 7.5-12.5a7.5 7.5 0 1 0-15 0C4.5 14.7 12 22 12 22Z"/><circle cx="12" cy="9.5" r="2.4"/>',
 'clock':'<circle cx="12" cy="12" r="9"/><path d="M12 6.5V12l3.5 2"/>',
 'document':'<path d="M6 2.5h9l4 4V21H6Z"/><path d="M15 2.5V7h4M9 12h7m-7 4h7"/>',
 'euro':'<path d="M19 7.8a7.2 7.2 0 1 0 0 8.5M3.5 10h10m-10 4h10"/>',
 'gear':'<path d="M10 2h4l.6 2.5 2.1.9 2.2-1.4 2.5 3-1.6 2.1.3 2.1 2.4 1.2-.8 4-2.7.2-1.1 1.7.5 2.6-3.6 1.4-1.8-2-2.2-.1-1.8 2-3.6-1.4.5-2.6-1.1-1.7-2.7-.2-.8-4 2.4-1.2.3-2.1-1.6-2.1 2.5-3 2.2 1.4 2.1-.9Z"/><circle cx="12" cy="12" r="3.1"/>',
 'leaf':'<path d="M21 3C9 3 3 7.5 3 15a6 6 0 0 0 6 6C16.5 21 21 15 21 3Z"/><path d="M7 17c3-4 7-7 11-9"/>',
 'check':'<path d="m4.5 12 4.7 4.5 10-10"/>',
 'shield':'<path d="m12 2 9 4v6c0 5-3 8-9 10-6-2-9-5-9-10V6Z"/><path d="m8 12 2.7 2.5 5-5"/>',
 'heart-handshake':'<path d="M2 9 6 5l6 2 4-2 6 6-4 4-3.5-2-4 5-4-2-3.5 1L2 9Z"/><path d="m8 10 5 4"/>',
 'arrow':'<path d="M3 12h17m-7-7 7 7-7 7"/>',
 'menu':'<path d="M3 6h18M3 12h18M3 18h18"/>',
 'close':'<path d="M5 5 19 19M19 5 5 19"/>',
}

def ic(name,cls='icon', extra=''):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" {extra}>{icons[name]}</svg>'

css=r'''/* CUENTAS CLARAS | reproducción del mockup - responsive y sin dependencias */
:root{--navy:#002743;--navy-rich:#042239;--navy-mid:#092c43;--navy-soft:#103c51;--green:#55c445;--green-bright:#6bdf52;--ink:#082b44;--muted:#5b7180;--pale:#f5f9fa;--line:#e0eaf0;--white:#fff;--shadow:0 12px 28px rgba(0,39,67,.10)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f7fafb;color:var(--ink);font:16px/1.55 'Segoe UI',Arial,Helvetica,sans-serif;-webkit-font-smoothing:antialiased}img{display:block;max-width:100%}a{color:inherit;text-decoration:none}button,input,textarea{font:inherit}button{cursor:pointer}.icon{width:24px;height:24px;display:inline-block;flex-shrink:0}.shell{max-width:1360px;margin:auto;background:white;min-height:100vh;overflow:hidden;box-shadow:0 0 38px rgba(0,22,39,.08)}.wrap{width:min(100% - 74px,1220px);margin:auto}
.header{position:relative;z-index:10;background:linear-gradient(110deg,#062f49,#052139 78%);color:#fff;box-shadow:0 4px 16px #0002}.navrow{min-height:84px;display:flex;justify-content:space-between;align-items:center;gap:25px}.brand{display:flex;align-items:center;gap:8px;flex-shrink:0}.brand-symbol{width:67px;height:67px;object-fit:contain;filter:drop-shadow(0 1px 2px #0003)}.brand-line{font-size:12px;line-height:1.05;letter-spacing:.05px;color:#fff;white-space:nowrap}.brand-name{font-size:25px;font-weight:780;line-height:1.07;letter-spacing:-.6px;color:white;white-space:nowrap}.brand-name span{color:var(--green)}.navigation{display:flex;align-items:center;gap:32px}.navlinks{display:flex;gap:31px;align-items:center}.navlinks a{font-size:13px;font-weight:700;color:#f5f8f9;padding:9px 0;border-bottom:2px solid transparent}.navlinks a:hover,.navlinks a.active{color:var(--green-bright);border-bottom-color:var(--green-bright)}.button{display:inline-flex;align-items:center;justify-content:center;gap:9px;border:0;border-radius:999px;min-height:42px;padding:11px 25px;background:linear-gradient(125deg,#60cd52,#37b13e);color:white;font-size:13px;font-weight:800;box-shadow:0 4px 8px #001c3512;transition:transform .18s,filter .18s}.button:hover{filter:brightness(1.07);transform:translateY(-1px)}.button .icon{width:16px;height:16px}.button-outline{color:#fff;background:transparent;border:1px solid #ffffff55}.button-small{min-height:39px;padding:10px 21px;white-space:nowrap}.menu-button{display:none;color:white;background:transparent;border:1px solid #ffffff55;border-radius:8px;width:43px;height:43px;align-items:center;justify-content:center}.menu-button .icon{width:25px;height:25px}
/* HERO */
.hero{position:relative;isolation:isolate;background:radial-gradient(circle at 41% 17%,#184966,#052139 72%);color:#fff;overflow:hidden}.hero-inner{position:relative;z-index:2}.hero-home{min-height:420px}.hero-home .hero-inner{display:grid;grid-template-columns:51% 49%;align-items:center;min-height:420px}.hero-home .hero-copy{padding:35px 22px 41px 0}.eyebrow{display:inline-block;color:#dbe7ed;letter-spacing:2px;font-size:13px;font-weight:780;text-transform:uppercase}.hero h1{font-size:clamp(43px,5.05vw,66px);line-height:1.055;letter-spacing:-1.5px;margin:14px 0 17px;font-weight:790}.hero h1 em{font-style:normal;color:var(--green-bright)}.hero p{max-width:515px;font-size:17px;line-height:1.48;color:#e6eff3;margin:0 0 15px}.hero-actions{display:flex;align-items:center;gap:13px;flex-wrap:wrap}.hero-link{font-size:13px;font-weight:700;display:inline-flex;gap:5px;align-items:center}.hero-link .icon{width:14px;height:14px;color:var(--green)}.hero-media{align-self:stretch;position:relative;min-height:360px;margin-right:calc((1220px - min(100vw - 74px,1220px))/-2)}.hero-media img{width:100%;height:100%;object-fit:cover;object-position:center;position:absolute;inset:0}.hero-media::before{content:"";position:absolute;z-index:1;inset:0;background:linear-gradient(90deg,#08283fc9 0%,#08283f2e 30%,transparent 74%)}.hero-home .hero-media img{object-position:center 47%}
/* HOME BAR */
.values-bar{background:linear-gradient(115deg,#052941,#062d44);color:white}.value-grid{display:grid;grid-template-columns:repeat(3,1fr);padding:27px 0 31px}.value{text-align:center;padding:4px 22px;border-right:1px solid #ffffff30}.value:last-child{border:0}.value .icon{width:55px;height:55px;color:var(--green-bright);stroke-width:1.65;margin:auto auto 9px}.value h2{font-size:20px;line-height:1.25;margin:0 0 8px}.value p{margin:0 auto;max-width:310px;color:#e0eaf0;font-size:13px;line-height:1.45}
/* AEROTHERMIA HOME */
.specialty-feature{display:grid;grid-template-columns:48% 52%;min-height:320px;background:#f7fbfc}.specialty-feature .photo{min-height:320px}.specialty-feature .photo img{width:100%;height:100%;object-fit:cover}.specialty-copy{display:flex;flex-direction:column;justify-content:center;padding:28px 9% 30px 8%}.specialty-copy h2{font-size:27px;line-height:1.2;color:#067329;margin:0 0 11px;font-weight:780}.specialty-copy p{font-size:14px;margin:0 0 10px;line-height:1.5}.tick-list{list-style:none;padding:0;margin:0 0 11px}.tick-list li{display:flex;gap:8px;align-items:flex-start;margin:5px 0;font-size:13px;line-height:1.45}.tick-list .icon{color:#20a348;width:18px;height:18px;margin-top:1px}.specialty-copy .button{align-self:flex-start}
/* WHY */
.why{background:#fff;padding:31px 0 27px}.why h2{text-align:center;font-size:24px;margin:0 0 22px}.benefits{display:grid;grid-template-columns:repeat(5,1fr)}.benefit{display:flex;flex-direction:column;align-items:center;text-align:center;gap:8px;padding:5px 15px;border-right:1px solid #d7e7ed}.benefit:last-child{border:0}.benefit .icon{width:31px;height:31px;color:#159d42}.benefit span{font-size:12px;line-height:1.3;font-weight:640;color:#092d47}
/* CTA PHOTO */
.cta-photo{position:relative;isolation:isolate;color:#fff;min-height:178px;display:flex;align-items:center;background:#05273b;overflow:hidden}.cta-photo::before{position:absolute;z-index:-2;content:"";inset:0;background:url('assets/aerotermia-jardin.jpg') center 53%/cover no-repeat;filter:saturate(.9)}.cta-photo::after{position:absolute;z-index:-1;content:"";inset:0;background:linear-gradient(90deg,#062a3b99,#07283ce8 37%,#092e44bd)}.cta-photo .wrap{padding:30px 0 30px 36%;}.cta-photo h2{font-size:21px;line-height:1.2;margin:0 0 5px}.cta-photo p{font-size:13px;color:#e9f1f2;margin:0 0 8px}
/* PAGE HERO */
.page-hero{min-height:288px;position:relative;overflow:hidden;background:linear-gradient(110deg,#06263e,#123b50);color:white;isolation:isolate}.page-hero::before{content:"";position:absolute;inset:0 0 0 48%;background:url('assets/aerotermia-cabecera.jpg') center 57%/cover no-repeat;z-index:-2}.page-hero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,#06253e 0%,#06253ee9 37%,#06253e63 67%,#06253e00 100%);z-index:-1}.page-hero .wrap{padding-top:49px;padding-bottom:45px}.page-hero h1{font-size:clamp(39px,4.6vw,57px);line-height:1.07;margin:11px 0 14px;letter-spacing:-1px}.page-hero p{max-width:525px;font-size:16px;color:#ecf3f4;line-height:1.48;margin:0}.page-hero .eyebrow{font-size:13px}
/* SERVICES GRID */
.services-area{background:#f6fafc;padding:27px 0 24px}.service-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:17px}.service-card{background:#fff;border-radius:8px;border:1px solid #e7eef1;box-shadow:var(--shadow);padding:22px 23px 19px;min-height:252px}.service-head{display:flex;align-items:center;gap:16px;margin-bottom:11px}.service-icon{display:grid;place-items:center;flex:0 0 57px;width:57px;height:57px;background:linear-gradient(140deg,#07324b,#001c35);border-radius:10px;box-shadow:0 3px 7px #00142624}.service-icon .icon{width:35px;height:35px;color:#82db68}.service-card h2{font-size:19px;line-height:1.18;margin:0;font-weight:780}.service-card ul{margin:0;padding:0;list-style:none}.service-card li{display:flex;gap:9px;align-items:flex-start;font-size:13px;line-height:1.42;margin:8px 0;color:#23445a}.service-card li .icon{color:#26a641;width:15px;height:15px;flex:0 0 15px;margin-top:2px}
.aero-banner{background:linear-gradient(100deg,#062c45,#093c46);border-radius:9px;min-height:257px;position:relative;isolation:isolate;overflow:hidden;color:#fff;display:flex;align-items:center;margin:22px 0 16px}.aero-banner::before{position:absolute;content:"";z-index:-2;inset:0 0 0 55%;background:url('assets/aerotermia-servicios.jpg') center/cover no-repeat}.aero-banner::after{position:absolute;content:"";z-index:-1;inset:0;background:linear-gradient(90deg,#052b43 0%,#052b43f5 48%,#052b43a3 68%,transparent 100%)}.aero-banner-copy{max-width:60%;padding:30px 32px}.aero-brand{display:flex;align-items:center;gap:17px}.circle-icon{background:var(--green);border-radius:50%;width:65px;height:65px;display:grid;place-items:center;color:#06354b;flex:0 0 65px}.circle-icon .icon{width:40px;height:40px}.aero-banner h2{margin:0 0 2px;font-size:25px;line-height:1.1}.aero-banner strong{color:#67d74d;font-size:14px}.aero-banner p{font-size:13px;line-height:1.45;max-width:400px;margin:11px 0}.aero-banner .button{margin-left:80px}.quality-footer{display:grid;grid-template-columns:repeat(3,1fr);gap:0;padding:24px 0;background:#fff}.quality{display:flex;align-items:center;gap:12px;justify-content:center;border-right:1px solid #e3edf1;padding:5px 10px}.quality:last-child{border-right:0}.quality .icon{width:30px;height:30px;color:#1ab34b}.quality span{font-size:12px;font-weight:750;line-height:1.25}
/* CONTACT */
.contact-hero{min-height:240px}.contact-hero::before{background:url('assets/edificio-detalle.jpg') center center/cover no-repeat;inset:0 0 0 45%}.contact-hero .wrap{padding:55px 0 44px}.contact-hero h1{font-size:51px}.contact-mini{position:absolute;right:6%;bottom:0;background:#073149e6;color:#fff;display:flex;gap:11px;align-items:center;padding:13px 18px;border-radius:9px 9px 0 0;max-width:308px}.contact-mini .circle-icon{width:47px;height:47px;flex:0 0 47px}.contact-mini .icon{width:29px;height:29px}.contact-mini b{font-size:13px;line-height:1.22;display:block}.contact-mini small{display:block;font-size:10px;margin-top:4px}
.contact-area{background:#fff;padding:28px 0 26px}.contact-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:27px}.contact-left{padding-right:0}.contact-right{border-left:1px solid #dfeaf0;padding-left:25px}.form-panel{border-radius:9px;background:linear-gradient(120deg,#f0f7fa,#f7fbfd);padding:25px 25px 20px}.form-panel h2{margin:0 0 7px;font-size:24px}.form-panel>p{font-size:13px;line-height:1.4;margin:0 0 11px;color:#315069}.form-grid{display:grid;grid-template-columns:1fr;gap:7px}.form-field label{display:block;font-size:12px;font-weight:780;margin:0 0 5px}.form-field input,.form-field textarea{width:100%;border-radius:3px;border:1px solid #d3dfe8;padding:11px 12px;background:#fff;color:#15394d;outline-color:#53c54a;font-size:14px}.form-field textarea{height:100px;resize:vertical}.form-panel .submit{width:100%;border-radius:4px;margin-top:9px}.form-hint{font-size:12px;min-height:15px;line-height:1.4;margin:9px 0 0;color:#607987}.form-hint.error{color:#b24738}
.contact-item{display:flex;align-items:flex-start;gap:16px;margin:8px 0 20px}.contact-item .icon{color:#23aa4a;width:28px;height:28px;margin-top:2px}.contact-item span{display:block;font-size:12px;color:#67819a;line-height:1.1}.contact-item strong,.contact-item a{font-size:15px;font-weight:750;line-height:1.25;overflow-wrap:anywhere}.contact-info{padding:6px 8px 0 5px;min-height:308px}.contact-location{border-top:1px solid #e8eff2;margin-top:20px;padding-top:20px}.contact-location h2{font-size:20px;margin:0 0 4px}.contact-location p{font-size:12px;color:#49708b;max-width:350px;line-height:1.35;margin:0 0 12px}.map-placeholder{height:217px;overflow:hidden;position:relative;border:1px solid #e2eaf0;background:#e9f0ea;border-radius:3px}.map-placeholder svg{width:100%;height:100%;display:block}.map-hint{position:absolute;bottom:10px;left:10px;right:10px;max-width:320px;color:#24445a;font-size:11px;background:#ffffffd9;padding:7px;border-radius:4px}.contact-side-aero{margin-top:8px;background:#eff9ed;border-radius:8px;padding:18px 17px}.contact-side-aero-head{display:flex;align-items:center;gap:12px}.contact-side-aero .circle-icon{width:42px;height:42px;flex:0 0 42px}.contact-side-aero .icon{width:26px;height:26px}.contact-side-aero h3{margin:0;font-size:18px;color:#07713a;line-height:1.13}.contact-side-aero p{font-size:13px;margin:10px 0}.contact-side-aero .button{padding:9px 18px;min-height:36px}.contact-side-photo{height:197px;margin-top:15px;border-radius:4px;object-fit:cover;width:100%}
.footer{background:linear-gradient(110deg,#06314b,#00253e);color:#fff}.footer-inner{min-height:95px;display:flex;align-items:center;justify-content:space-between;gap:18px}.footer .brand-symbol{width:50px;height:50px}.footer .brand-line{font-size:9px}.footer .brand-name{font-size:18px}.footer nav{display:flex;align-items:center;gap:26px;font-size:12px}.footer nav a:hover{color:var(--green)}.footer-end{font-size:12px;display:flex;align-items:center;gap:12px;text-align:right}.footer-end .icon{color:var(--green);width:31px;height:31px}
/* Responsividad imitando los teléfonos mostrados en el mockup */
@media(max-width:1100px){.wrap{width:calc(100% - 54px)}.navigation{gap:16px}.navlinks{gap:18px}.hero-home .hero-inner{grid-template-columns:51% 49%}.hero h1{font-size:51px}.value h2{font-size:18px}.aero-banner-copy{max-width:65%}}
@media(max-width:780px){.wrap{width:calc(100% - 38px)}.navrow{min-height:74px}.brand-symbol{width:53px;height:53px}.brand-line{font-size:10px}.brand-name{font-size:20px}.menu-button{display:flex}.navigation{display:none;position:absolute;top:100%;left:0;right:0;background:#052c44;padding:18px 20px 23px;box-shadow:0 12px 20px #0003;flex-direction:column;align-items:stretch}.navigation.open{display:flex}.navlinks{align-items:stretch;flex-direction:column;gap:0}.navlinks a{padding:13px 0;border-bottom:1px solid #ffffff22}.navigation .button{margin-top:12px}.hero-home{min-height:0}.hero-home .hero-inner{display:flex;min-height:530px;align-items:flex-end}.hero-home .hero-copy{position:relative;z-index:2;width:100%;padding:105px 0 54px}.hero-home .hero-media{position:absolute;inset:0;min-height:100%;margin:0}.hero-home .hero-media::before{background:linear-gradient(90deg,#052942e8 0%,#052942a1 60%,#0529427a),linear-gradient(0deg,#052942de,transparent 62%)}.hero-home .hero-media img{object-position:60%}.hero h1{font-size:53px}.hero p{font-size:16px;max-width:480px}.values-bar .value-grid{padding:17px 0 19px}.value{padding:4px 9px}.value .icon{width:38px;height:38px}.value h2{font-size:14px}.value p{font-size:11px}.specialty-feature{grid-template-columns:1fr;min-height:0}.specialty-feature .photo{height:250px;min-height:0}.specialty-copy{padding:25px 6% 29px}.specialty-copy h2{font-size:25px}.why h2{font-size:22px}.benefit{padding:5px 5px}.benefit span{font-size:10px}.benefit .icon{width:25px;height:25px}.cta-photo .wrap{padding:35px 0 35px 20%}.page-hero h1{font-size:47px}.service-grid{grid-template-columns:1fr}.service-card{min-height:0}.aero-banner-copy{max-width:76%}.contact-grid{grid-template-columns:1fr}.contact-right{border:0;padding:0}.contact-info{display:grid;grid-template-columns:1fr 1fr;min-height:0;padding:0}.contact-mini{display:none}.contact-hero{min-height:0}.contact-hero .wrap{padding:58px 0}.contact-right{display:grid;grid-template-columns:1fr 1fr;gap:20px}.contact-info,.contact-side-aero{grid-column:span 1}.contact-location{grid-column:1/-1}.contact-side-photo{grid-column:2;margin-top:0;height:240px}.footer-inner{gap:14px}.footer nav{gap:12px}.footer-end{font-size:10px}}
@media(max-width:520px){.navrow{min-height:67px}.brand-symbol{width:48px;height:48px}.brand-name{font-size:18px}.brand-line{font-size:9px}.menu-button{width:41px;height:41px}.hero-home .hero-inner{min-height:480px}.hero-home .hero-copy{padding:75px 0 30px}.hero h1{font-size:42px;letter-spacing:-.9px;margin:12px 0 13px}.hero p{font-size:14px}.eyebrow{font-size:11px;letter-spacing:1.2px}.hero-actions .button{font-size:12px;padding:10px 17px;min-height:39px}.hero-link{font-size:12px}.values-bar .value-grid{width:100%;padding:16px 5px;gap:0}.value{padding:0 5px}.value .icon{width:33px;height:33px;margin-bottom:4px}.value h2{font-size:11.5px;line-height:1.15}.value p{font-size:9.5px}.specialty-feature .photo{height:205px}.specialty-copy h2{font-size:22px}.why{padding:25px 0}.why h2{font-size:21px;margin-bottom:15px}.benefits{grid-template-columns:repeat(5,1fr)}.benefit .icon{width:23px;height:23px}.benefit span{font-size:9.4px}.cta-photo{min-height:180px}.cta-photo .wrap{padding:23px 0 24px 8%}.cta-photo h2{font-size:18px}.page-hero{min-height:235px}.page-hero .wrap{padding:38px 0}.page-hero h1{font-size:39px}.page-hero p{font-size:14px;max-width:80%}.page-hero::before{inset:0 0 0 37%}.service-card{padding:20px}.service-head{gap:13px}.service-icon{width:51px;height:51px;flex-basis:51px}.service-card h2{font-size:17px}.service-card li{font-size:12px}.aero-banner{min-height:290px}.aero-banner::before{inset:0 0 0 20%;opacity:.60}.aero-banner::after{background:linear-gradient(90deg,#052b43 0%,#052b43d9 70%,#052b4388)}.aero-banner-copy{max-width:100%;padding:20px}.aero-brand{gap:11px}.circle-icon{width:51px;height:51px;flex-basis:51px}.circle-icon .icon{width:33px;height:33px}.aero-banner h2{font-size:21px}.aero-banner strong{font-size:12px}.aero-banner p{font-size:12px;max-width:310px}.aero-banner .button{margin-left:0}.quality-footer{padding:14px 0}.quality{flex-direction:column;text-align:center;gap:5px;padding:2px 5px}.quality .icon{width:24px;height:24px}.quality span{font-size:9px}.contact-hero h1{font-size:39px}.contact-hero p{max-width:70%}.contact-area{padding:20px 0}.form-panel{padding:21px 16px}.form-panel h2{font-size:22px}.contact-right{display:block}.contact-info{display:block;min-height:0}.contact-item{margin:9px 0 16px}.contact-side-aero{margin-top:20px}.contact-side-photo{height:190px;margin-top:13px}.map-placeholder{height:190px}.footer-inner{min-height:0;padding:21px 0;display:grid;grid-template-columns:1fr auto;row-gap:15px}.footer .brand-name{font-size:16px}.footer nav{grid-row:2;grid-column:1/-1;justify-content:center}.footer-end{grid-column:2;grid-row:1;text-align:right;font-size:9px}.footer-end .icon{width:22px;height:22px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition:none!important}}
'''
(OUT/'styles.css').write_text(css,encoding='utf-8')

js=r'''/* Menú móvil y formulario de demostración. Personalizar CONTACT_EMAIL para activarlo. */
const CONTACT_EMAIL=''; // Ejemplo: 'hola@tudominio.es' (no inventar datos de la empresa)
document.addEventListener('DOMContentLoaded',()=>{
 const btn=document.querySelector('[data-menu-toggle]');
 const menu=document.querySelector('[data-mobile-navigation]');
 if(btn&&menu){
  btn.addEventListener('click',()=>{const open=menu.classList.toggle('open');btn.setAttribute('aria-expanded',String(open));btn.setAttribute('aria-label',open?'Cerrar menú':'Abrir menú');btn.innerHTML=open?window.MENU_CLOSE_ICON:window.MENU_OPEN_ICON;});
  menu.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{menu.classList.remove('open');btn.setAttribute('aria-expanded','false');btn.setAttribute('aria-label','Abrir menú');btn.innerHTML=window.MENU_OPEN_ICON;}));
 }
 const form=document.querySelector('#formulario-contacto');
 if(form){form.addEventListener('submit',e=>{
  e.preventDefault();const output=document.querySelector('#form-status');
  if(!CONTACT_EMAIL){output.textContent='Para enviar consultas, configura el correo de la empresa en app.js o inserta Google Forms.';output.classList.add('error');return;}
  const data=new FormData(form);const subject=encodeURIComponent('Consulta desde Cuentas Claras');
  const body=encodeURIComponent('Nombre: '+(data.get('nombre')||'')+'\nEmail: '+(data.get('email')||'')+'\nTeléfono: '+(data.get('telefono')||'')+'\nComunidad: '+(data.get('comunidad')||'')+'\n\nMensaje:\n'+(data.get('mensaje')||''));
  window.location.href='mailto:'+CONTACT_EMAIL+'?subject='+subject+'&body='+body;
  output.textContent='Se ha abierto tu aplicación de correo para enviar la consulta.';output.classList.remove('error');
 });}
});
'''
(OUT/'app.js').write_text(js,encoding='utf-8')

# Build a generic schematic map - no fabricated office address or pinpoint.
map_svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 360" preserveAspectRatio="xMidYMid slice" aria-label="Mapa ilustrativo, dirección pendiente" role="img"><rect width="720" height="360" fill="#eef3ed"/><g fill="#bcdca9"><path d="M0 0h145v98H0zM510 18h175v94H510zM525 244h195v116H525zM0 258h115v102H0z"/></g><g fill="#dfe5d9"><path d="M185 22h190v72H185zM288 210h160v76H288zM53 145h140v65H53z"/></g><g stroke="#fff" stroke-width="24" fill="none"><path d="M0 105 720 260M120 0 390 360M0 290 720 65M540 0 455 360M0 180 720 180"/></g><g stroke="#bdcbd0" stroke-width="3" fill="none"><path d="M0 105 720 260M120 0 390 360M0 290 720 65M540 0 455 360M0 180 720 180"/></g><g stroke="#c3d0cc" stroke-width="4" fill="none"><path d="M70 0v360M210 0v360M600 0v360M0 50h720M0 330h720"/></g></svg>'''
(OUT/'assets'/'mapa-ilustrativo.svg').write_text(map_svg,encoding='utf-8')

brand=lambda: f'''<a class="brand" href="index.html" aria-label="Cuentas Claras, ir al inicio"><img src="assets/isotipo-cuentas-claras.webp" alt="" class="brand-symbol"/><span><span class="brand-line">Administrador de Fincas</span><br/><span class="brand-name">Cuentas <span>Claras</span></span></span></a>'''

def layout(active,title,body):
    links=''.join(f'<a href="{file}" class="{"active" if active==name else ""}" {"aria-current=page" if active==name else ""}>{name}</a>' for name,file in [('Inicio','index.html'),('Servicios','servicios.html'),('Contacto','contacto.html')])
    header=f'''<header class="header"><div class="wrap navrow">{brand()}<div class="navigation" id="site-navigation" data-mobile-navigation><nav class="navlinks" aria-label="Menú principal">{links}</nav><a class="button button-small" href="contacto.html">Solicita información {ic('arrow')}</a></div><button class="menu-button" data-menu-toggle aria-controls="site-navigation" aria-expanded="false" aria-label="Abrir menú">{ic('menu')}</button></div></header>'''
    footer=f'''<footer class="footer"><div class="wrap footer-inner">{brand()}<nav aria-label="Enlaces de pie de página"><a href="index.html">Inicio</a><a href="servicios.html">Servicios</a><a href="contacto.html">Contacto</a></nav><div class="footer-end">Tu comunidad,<br/>en buenas manos. {ic('check')}</div></div></footer>'''
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><meta name="theme-color" content="#052d46"/><meta name="description" content="Administrador de Fincas Cuentas Claras. Gestión honesta, transparente y especializada en comunidades con aerotermia."/><title>{title} | Administrador de Fincas Cuentas Claras</title><link rel="stylesheet" href="styles.css"/></head><body><div class="shell">{header}<main>{body}</main>{footer}</div><script>window.MENU_CLOSE_ICON={json.dumps(ic('close'))};window.MENU_OPEN_ICON={json.dumps(ic('menu'))};</script><script defer src="app.js"></script></body></html>'''

home_values=[('honestidad','Honestidad','Sin sorpresas, sin letra pequeña. Siempre de tu lado.'),('eye','Transparencia','Información clara y accesible en todo momento.'),('aero','Especialistas en comunidades con aerotermia','Más eficiencia, menos costes, mayor sostenibilidad.')]
benefits=[('document','Cuentas claras<br/>y comprensibles'),('euro','Sin sorpresas<br/>ni letra pequeña'),('bolt','Especialistas en<br/>aerotermia'),('gear','Seguimiento<br/>de proveedores'),('users','Atención cercana<br/>al propietario')]
values=''.join(f'<div class="value">{ic(t)}<h2>{h}</h2><p>{d}</p></div>' for t,h,d in home_values)
benefits_markup=''.join(f'<div class="benefit">{ic(t)}<span>{d}</span></div>' for t,d in benefits)

home=f'''
<section class="hero hero-home"><div class="wrap hero-inner"><div class="hero-copy"><span class="eyebrow">Administrador de fincas</span><h1>Tu comunidad,<br/>bien gestionada.<br/><em>Cuentas claras.</em></h1><p>Gestión profesional, honesta y transparente de tu comunidad de propietarios.</p><div class="hero-actions"><a class="button" href="contacto.html">Solicita información {ic('arrow')}</a><a class="hero-link" href="servicios.html">Nuestros servicios {ic('arrow')}</a></div></div><div class="hero-media"><img src="assets/residencial-hero.jpg" alt="Edificio residencial moderno con terrazas de cristal y jardines" fetchpriority="high"/></div></div></section>
<section class="values-bar" aria-label="Nuestros valores"><div class="wrap value-grid">{values}</div></section>
<section class="specialty-feature" aria-labelledby="aero-home"><div class="photo"><img src="assets/aerotermia-jardin.jpg" alt="Equipo exterior de aerotermia entre plantas y árboles" loading="lazy"/></div><div class="specialty-copy"><h2 id="aero-home">Especialistas en comunidades con aerotermia</h2><p>Te ayudamos a sacar el máximo rendimiento a tu sistema de aerotermia, con una gestión experta y un control eficiente del consumo.</p><ul class="tick-list"><li>{ic('check')} Optimización del consumo energético</li><li>{ic('check')} Seguimiento y mantenimiento de la instalación</li><li>{ic('check')} Gestión de contratos y suministros</li></ul><a class="button" href="servicios.html#especialistas-aerotermia">Saber más sobre aerotermia {ic('arrow')}</a></div></section>
<section class="why"><div class="wrap"><h2>¿Por qué elegir Cuentas Claras?</h2><div class="benefits">{benefits_markup}</div></div></section>
<section class="cta-photo"><div class="wrap"><h2>¿Quieres una gestión más transparente<br/>de tu comunidad?</h2><p>Solicita una primera consulta sin compromiso.</p><a class="button" href="contacto.html">Solicita información {ic('arrow')}</a></div></section>
'''

service_items=[
('calculator','Gestión administrativa y contable',[
'Gestión contable de la Comunidad.',
'Elaboración del presupuesto anual y seguimiento del gasto.',
'Emisión, gestión y control de recibos.',
'Gestión de cobros y seguimiento de la morosidad.',
'Elaboración de informes económicos periódicos.'
]),
('building','Gestión de elementos comunes',[
'Seguimiento del estado general del edificio.',
'Gestión de proveedores y control de servicios contratados (ascensores, limpieza, etc.).',
'Asesoramiento y tramitación de pólizas de seguros.',
'Tramitación de incidencias y averías.',
'Solicitud y estudio de presupuestos para trabajos.'
]),
('bolt','Suministros y contratos',[
'Tramitación y gestión de altas de suministros.',
'Análisis y revisión de contratos existentes.',
'Control y seguimiento de la facturación de servicios.',
'Gestión de renovaciones y actualización de contratos vigentes.'
]),
('users','Asesoramiento y gestión general',[
'Asesoramiento legal y técnico básico en materia de propiedad horizontal.',
'Atención a propietarios y resolución de consultas.',
'Notificación a propietarios por medios ordinarios y telemáticos.',
'Custodia, organización y archivo de la documentación de la Comunidad.'
])]
service_cards=''.join(f'''<article class="service-card"><div class="service-head"><div class="service-icon">{ic(icon)}</div><h2>{name}</h2></div><ul>{''.join(f'<li>{ic('check')}{item}</li>' for item in li)}</ul></article>''' for icon,name,li in service_items)
quality=''.join(f'<div class="quality">{ic(icon)}<span>{text}</span></div>' for icon,text in [('users','Experiencia<br/>y profesionalidad'),('heart-handshake','Trato personal<br/>y cercano'),('document','Soluciones a medida<br/>para cada comunidad')])
services=f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">Nuestros servicios</span><h1>Gestión integral<br/>para tu comunidad</h1><p>Ofrecemos un servicio completo y personalizado, adaptado a las necesidades de cada comunidad de propietarios.</p></div></section>
<section class="services-area"><div class="wrap"><div class="service-grid">{service_cards}</div><div class="aero-banner" id="especialistas-aerotermia"><div class="aero-banner-copy"><div class="aero-brand"><div class="circle-icon">{ic('leaf')}</div><div><h2>Aerotermia</h2><strong>Eficiencia energética para tu comunidad</strong></div></div><p>Somos especialistas en comunidades con aerotermia. Te ayudamos a optimizar su funcionamiento, reducir costes y garantizar su mantenimiento.</p><a class="button" href="contacto.html">Más información sobre aerotermia {ic('arrow')}</a></div></div></div><div class="quality-footer wrap">{quality}</div></section>
'''
contact_details=''.join(f'<div class="contact-item">{ic(symbol)}<div><span>{key}</span><strong>{val}</strong></div></div>' for symbol,key,val in [('phone','Teléfono','[TELÉFONO]'),('mail','Email','[EMAIL]'),('pin','Dirección','[DIRECCIÓN DE LA OFICINA]'),('clock','Horario','[HORARIO DE ATENCIÓN]')])
contact=f'''
<section class="page-hero contact-hero"><div class="wrap"><span class="eyebrow">Contacto</span><h1>Hablemos de tu comunidad</h1><p>Estamos a tu disposición para resolver tus dudas y ayudarte a gestionar tu finca con total transparencia.</p></div><aside class="contact-mini"><div class="circle-icon">{ic('leaf')}</div><div><b>Especialistas en comunidades con aerotermia</b><small>Solicita asesoramiento personalizado.</small></div></aside></section>
<section class="contact-area"><div class="wrap contact-grid"><div class="contact-left"><div class="form-panel"><h2>Envíanos un mensaje</h2><p>Rellena el formulario y nos pondremos en contacto contigo lo antes posible.</p><form id="formulario-contacto"><div class="form-grid"><div class="form-field"><label for="nombre">Nombre *</label><input id="nombre" name="nombre" autocomplete="name" required/></div><div class="form-field"><label for="email">Email *</label><input id="email" name="email" type="email" autocomplete="email" required/></div><div class="form-field"><label for="telefono">Teléfono</label><input id="telefono" name="telefono" type="tel" autocomplete="tel"/></div><div class="form-field"><label for="comunidad">Comunidad</label><input id="comunidad" name="comunidad" autocomplete="organization"/></div><div class="form-field"><label for="mensaje">Mensaje *</label><textarea id="mensaje" name="mensaje" required></textarea></div></div><button class="button submit" type="submit">Enviar mensaje {ic('arrow')}</button><p class="form-hint" id="form-status" role="status"></p></form></div><div class="contact-location"><h2>Nuestra ubicación</h2><p>Puedes encontrarnos en nuestra oficina o ponerte en contacto por los medios indicados.</p><div class="map-placeholder"><svg viewBox="0 0 720 360" role="img" aria-label="Mapa ilustrativo de calles, no indica una dirección real"><use href="assets/mapa-ilustrativo.svg#map"></use></svg><div class="map-hint">Ubicación pendiente de indicar</div></div></div></div><div class="contact-right"><div class="contact-info">{contact_details}</div><div class="contact-side-aero"><div class="contact-side-aero-head"><div class="circle-icon">{ic('leaf')}</div><h3>¿Tu comunidad<br/>tiene aerotermia?</h3></div><p>Somos especialistas en la gestión de comunidades con aerotermia. Te ayudamos a sacar el máximo rendimiento.</p><a class="button" href="servicios.html#especialistas-aerotermia">Solicita asesoramiento {ic('arrow')}</a></div><img class="contact-side-photo" src="assets/edificio-contacto.jpg" alt="Edificio de viviendas contemporáneo rodeado de árboles" loading="lazy"/></div></div></section>
'''
# Fix map rendering by inlining SVG: external references to SVG were problematic in prior version.
contact=contact.replace('<svg viewBox="0 0 720 360" role="img" aria-label="Mapa ilustrativo de calles, no indica una dirección real"><use href="assets/mapa-ilustrativo.svg#map"></use></svg>',map_svg)
for filename,active,title,body in [
 ('index.html','Inicio','Inicio',home),('servicios.html','Servicios','Servicios',services),('contacto.html','Contacto','Contacto',contact)]:
    (OUT/filename).write_text(layout(active,title,body),encoding='utf-8')

(OUT/'LEEME.txt').write_text('''ADMINISTRADOR DE FINCAS CUENTAS CLARAS — VERSIÓN FIEL A LOS MOCKUPS

ESTRUCTURA:
- index.html: INICIO, reproduce hero con edificio, 3 ventajas, foto aerotermia, sección de beneficios y CTA
- servicios.html: hero aerotermia, 4 tarjetas con todos los servicios, banner aerotermia y franja inferior
- contacto.html: hero edificio, formulario, datos de contacto, mapa ilustrativo y bloque aerotermia
- styles.css: diseño desktop + móvil, construido sin frameworks
- app.js: menú desplegable y envío por cliente de correo cuando se configure
- assets/: fotografías extraídas de las composiciones de mockup facilitadas y recortadas para el diseño; logo basado en el original.
- PREVISUALIZACIONES/: imágenes capturadas de la web renderizada, tanto en escritorio como en móvil.

ICONOS: se han incrustado de forma inline en los tres HTML, evitando la incidencia de versiones anteriores.

PARA VER LA WEB: descomprime y abre index.html; funciona sin conexión a Internet.

ANTES DE PUBLICAR:
1. Edita los datos [TELÉFONO], [EMAIL], [DIRECCIÓN DE LA OFICINA] y [HORARIO DE ATENCIÓN] en contacto.html.
2. En app.js, sustituye CONTACT_EMAIL='' por el correo de atención al cliente. El formulario entonces abrirá el cliente de correo de la persona que lo envíe; NO envía por servidor. Para envío real con confirmación se recomienda integrar Google Forms u otro backend.
3. Sustituye el mapa ilustrativo por un mapa real una vez se conozca la ubicación de la empresa.
4. Las fotografías están basadas en recortes de las imágenes originales de los mockups. Se corresponden visualmente con los mockups, pero no son fotografías fuente de alta resolución; si consigues las fotografías originales, puedes reemplazarlas por archivos de mayor calidad.

GOOGLE SITES: este HTML independiente NO se importa directamente como plantilla nativa editable de Google Sites. Se puede alojar como web externa o usar como base de reconstrucción dentro de Sites.
''',encoding='utf-8')

print('Created site files:')
for p in OUT.rglob('*'):
 if p.is_file():print(p.relative_to(OUT),p.stat().st_size)
