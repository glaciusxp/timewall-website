const menu=document.querySelector('.menu-toggle');
const nav=document.querySelector('#navigation');
menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open)});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav?.classList.contains('open')){nav.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.focus()}});
const dialog=document.querySelector('.lightbox');
if(dialog&&typeof dialog.showModal==='function'){
 document.querySelectorAll('[data-lightbox]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();const img=dialog.querySelector('img');img.src=a.href;img.alt=a.querySelector('img')?.alt||'';dialog.showModal()}));
 dialog.querySelector('button').addEventListener('click',()=>dialog.close());
 dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
}
