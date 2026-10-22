import re, json
LOGO = "https://innovasites.co/wp-content/uploads/2024/03/INNOVA-03-03.png"
WA = "https://api.whatsapp.com/send/?phone=573024617516"
DISP = "'Oswald','Arial Narrow',Arial,Helvetica,sans-serif"
BODY = "Arial,Helvetica,sans-serif"
MONO = "'Courier New',Courier,monospace"

def header(label):
    return f'''<tr><td style="background:#0A0C11;padding:22px 32px;border-bottom:3px solid #E5342A;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td style="vertical-align:middle;"><img src="{LOGO}" width="34" height="34" alt="" style="display:inline-block;vertical-align:middle;border:0;"><span style="display:inline-block;vertical-align:middle;margin-left:10px;font-family:{DISP};font-size:20px;font-weight:700;font-style:italic;letter-spacing:.5px;color:#ffffff;">INNOVA<span style="color:#E5342A;">SITES</span></span></td>
<td align="right" style="vertical-align:middle;font-family:{MONO};font-size:11px;letter-spacing:2px;color:#FF5A45;text-transform:uppercase;">{label}</td>
</tr></table></td></tr>'''

def wrap(preheader, rows):
    return f'''<div style="margin:0;padding:0;background:#EDEEF1;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">{preheader}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#EDEEF1;"><tr><td align="center" style="padding:28px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;background:#ffffff;">
{rows}
</table>
</td></tr></table></div>'''

def footer(extra):
    return f'''<tr><td style="background:#0A0C11;padding:26px 32px;">
<p style="margin:0 0 6px;font-family:{DISP};font-size:18px;font-weight:700;font-style:italic;text-transform:uppercase;color:#ffffff;">Cada pixel <span style="color:#E5342A;">cuenta.</span></p>
<p style="margin:0 0 14px;font-family:{BODY};font-size:13px;line-height:20px;color:#A9AFBB;">Sitios web, apps y contenido desde Cali para toda Latinoamérica.</p>
<p style="margin:0;font-family:{BODY};font-size:13px;line-height:22px;"><a href="https://innovasites.co" style="color:#ffffff;text-decoration:none;">innovasites.co</a><span style="color:#6B7180;">&nbsp;&nbsp;·&nbsp;&nbsp;</span><a href="https://www.instagram.com/innova_sites/" style="color:#ffffff;text-decoration:none;">Instagram</a><span style="color:#6B7180;">&nbsp;&nbsp;·&nbsp;&nbsp;</span><a href="https://www.tiktok.com/@innova.sites" style="color:#ffffff;text-decoration:none;">TikTok</a><span style="color:#6B7180;">&nbsp;&nbsp;·&nbsp;&nbsp;</span><a href="https://www.facebook.com/profile.php?id=61555191832402" style="color:#ffffff;text-decoration:none;">Facebook</a></p>
{extra}
</td></tr>'''

def row(label, value, pre=False):
    ws = "white-space:pre-wrap;" if pre else ""
    return f'''<tr><td style="padding:14px 0;border-bottom:1px solid #ECECEF;">
<p style="margin:0 0 4px;font-family:{MONO};font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#8C92A1;">{label}</p>
<p style="margin:0;font-family:{BODY};font-size:16px;line-height:24px;color:#0A0C11;{ws}">{value}</p></td></tr>'''

def button(href, text, bg="#E5342A", color="#ffffff"):
    return f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="display:inline-table;margin:0 8px 8px 0;"><tr><td style="background:{bg};"><a href="{href}" style="display:inline-block;padding:14px 22px;font-family:{DISP};font-size:15px;font-weight:700;font-style:italic;letter-spacing:1px;text-transform:uppercase;color:{color};text-decoration:none;">{text} &rarr;</a></td></tr></table>'''

# ---------- correo para InnovaSites ----------
team = wrap("[your-name] escribió desde la web. Responde en menos de 24 horas.", header("Nuevo contacto") + f'''
<tr><td style="padding:34px 32px 8px;">
<p style="margin:0 0 6px;font-family:{MONO};font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#E5342A;">&#9632; Formulario de innovasites.co</p>
<h1 style="margin:0 0 10px;font-family:{DISP};font-size:34px;line-height:38px;font-weight:700;font-style:italic;text-transform:uppercase;color:#0A0C11;">[your-name] quiere hablar</h1>
<p style="margin:0;font-family:{BODY};font-size:15px;line-height:23px;color:#4A5060;">Llegó el [_date] a las [_time] y le prometimos respuesta en menos de 24 horas.</p>
</td></tr>
<tr><td style="padding:22px 32px 6px;">{button("mailto:[your-email]", "Responder por correo")}</td></tr>
<tr><td style="padding:10px 32px 30px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
{row("Nombre", "[your-name]")}
{row("Correo", '<a href="mailto:[your-email]" style="color:#E5342A;text-decoration:none;">[your-email]</a>')}
{row("Negocio o marca", "[your-business]")}
{row("Mensaje y servicios de interés", "[your-message]", pre=True)}
</table></td></tr>''' + footer(f'<p style="margin:14px 0 0;font-family:{BODY};font-size:11px;line-height:17px;color:#6B7180;">Enviado desde [_url]. Si respondes a este correo, la respuesta le llega directo a [your-name].</p>'))

# ---------- correo para el cliente ----------
def step(n, title, text):
    return f'''<tr><td width="46" valign="top" style="padding:0 0 18px;"><div style="width:34px;height:34px;line-height:34px;text-align:center;background:#E5342A;font-family:{DISP};font-size:16px;font-weight:700;font-style:italic;color:#ffffff;">{n}</div></td>
<td valign="top" style="padding:0 0 18px;"><p style="margin:0 0 3px;font-family:{DISP};font-size:17px;font-weight:700;font-style:italic;text-transform:uppercase;color:#0A0C11;">{title}</p><p style="margin:0;font-family:{BODY};font-size:14px;line-height:21px;color:#4A5060;">{text}</p></td></tr>'''

client = wrap("Recibimos tu mensaje. Te respondemos en menos de 24 horas.", header("Mensaje recibido") + f'''
<tr><td style="background:#0A0C11;padding:40px 32px 36px;">
<p style="margin:0 0 10px;font-family:{MONO};font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#FF5A45;">&#9632; Hola, [your-name]</p>
<h1 style="margin:0 0 14px;font-family:{DISP};font-size:40px;line-height:42px;font-weight:700;font-style:italic;text-transform:uppercase;color:#ffffff;">Tu proyecto ya está <span style="color:#E5342A;">en nuestras manos.</span></h1>
<p style="margin:0;font-family:{BODY};font-size:16px;line-height:25px;color:#C9CDD6;">Gracias por escribirnos. Ya recibimos tu mensaje y lo estamos leyendo con calma. <strong style="color:#ffffff;">Te respondemos en menos de 24 horas</strong> con una idea clara de cómo podemos ayudarte.</p>
</td></tr>
<tr><td style="padding:32px 32px 8px;">
<p style="margin:0 0 18px;font-family:{MONO};font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#E5342A;">Qué sigue</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
{step("1", "Revisamos tu idea", "Leemos lo que nos contaste sobre tu negocio y tu público.")}
{step("2", "Te escribimos", "En menos de 24 horas, por correo o WhatsApp, para aclarar lo que haga falta.")}
{step("3", "Propuesta clara", "Alcance, tiempos y costo por escrito en 2 a 3 días. Sin letra chica.")}
</table></td></tr>
<tr><td style="padding:8px 32px 30px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#F5F5F7;border-left:3px solid #E5342A;"><tr><td style="padding:18px 20px;">
<p style="margin:0 0 6px;font-family:{MONO};font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#8C92A1;">Lo que nos contaste</p>
<p style="margin:0;font-family:{BODY};font-size:15px;line-height:23px;color:#0A0C11;white-space:pre-wrap;">[your-message]</p>
</td></tr></table></td></tr>
<tr><td style="padding:0 32px 34px;">
<p style="margin:0 0 14px;font-family:{BODY};font-size:15px;line-height:23px;color:#4A5060;">¿Te urge? Escríbenos directo y lo vemos de una vez.</p>
{button(WA, "Escribir por WhatsApp")}{button("https://innovasites.co", "Ver innovasites.co", bg="#0A0C11")}
</td></tr>''' + footer(f'<p style="margin:14px 0 0;font-family:{BODY};font-size:11px;line-height:17px;color:#6B7180;">Recibes este correo porque escribiste en el formulario de innovasites.co. Si no fuiste tú, ignóralo. Puedes responder a este correo para hablar con nosotros.</p>'))

def flat(s):
    s = re.sub(r'\n+', '', s)
    assert '\n' not in s
    return s
open('team.html','w').write(flat(team)); open('client.html','w').write(flat(client))
sample = {'[your-name]':'Laura Gómez','[your-email]':'laura@cafeorigen.co','[your-business]':'Café Origen','[your-message]':'Quiero renovar la web de mi café y vender en línea.\n\nServicios de interés: Sitio web, Redes sociales','[_date]':'22 de octubre de 2026','[_time]':'6:05 p. m.','[_url]':'https://innovasites.co/'}
for name in ('team','client'):
    s=open(name+'.html').read()
    for k,v in sample.items(): s=s.replace(k,v)
    open(name+'-preview.html','w').write('<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0">'+s+'</body></html>')
print(len(open('team.html').read()), len(open('client.html').read()))
