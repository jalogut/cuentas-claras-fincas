/* Menú móvil y formulario de demostración. Personalizar CONTACT_EMAIL para activarlo. */
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
