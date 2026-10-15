'use strict';
document.documentElement.classList.add('enhanced');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

document.querySelectorAll('[data-dismiss]').forEach(button => {
  button.addEventListener('click', () => button.closest('.alert').remove());
});
document.querySelectorAll('[data-toggle-password]').forEach(button => {
  button.addEventListener('click', () => {
    const input = document.getElementById(button.dataset.togglePassword);
    const visible = input.type === 'password';
    input.type = visible ? 'text' : 'password';
    button.setAttribute('aria-label', visible ? 'Ocultar contraseña' : 'Mostrar contraseña');
    button.setAttribute('aria-pressed', String(visible));
  });
});
document.querySelectorAll('[data-counter]').forEach(input => {
  const output = input.closest('.field').querySelector('[data-counter-output]');
  const update = () => { output.textContent = `${input.value.length} / ${input.maxLength}`; };
  input.addEventListener('input', update);
  update();
});
document.querySelectorAll('[data-password-new]').forEach(input => {
  const bar = input.closest('.field').querySelector('.password-meter span');
  input.addEventListener('input', () => {
    const value = input.value;
    const score = [value.length >= 10, /[A-Za-z]/.test(value), /[0-9]/.test(value), value.length >= 16].filter(Boolean).length;
    bar.style.width = value ? `${score * 25}%` : '0';
  });
});

document.querySelectorAll('[data-wizard]').forEach(form => {
  const panels = [...form.querySelectorAll('[data-step]')];
  const labels = [...form.querySelectorAll('[data-step-label]')];
  const next = form.querySelector('[data-next]');
  const back = form.querySelector('[data-back]');
  const submit = form.querySelector('[data-submit]');
  const error = form.querySelector('[data-form-error]');
  let current = 0;
  const show = (index, focus = false) => {
    current = index;
    panels.forEach((panel, i) => { panel.hidden = i !== index; });
    labels.forEach((label, i) => {
      label.classList.toggle('active', i === index);
      label.classList.toggle('done', i < index);
      if (i === index) label.setAttribute('aria-current', 'step');
      else label.removeAttribute('aria-current');
    });
    back.hidden = index === 0;
    next.hidden = index === panels.length - 1;
    submit.hidden = index !== panels.length - 1;
    error.textContent = '';
    if (focus) {
      const heading = panels[index].querySelector('h2,h3');
      heading.setAttribute('tabindex', '-1');
      heading.focus({ preventScroll: true });
      form.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    }
  };
  const validate = index => {
    const password = form.querySelector('[data-password-new]');
    const confirmation = form.querySelector('[data-password-confirm]');
    if (password) {
      password.setCustomValidity(password.value && (!/[A-Za-z]/.test(password.value) || !/[0-9]/.test(password.value)) ? 'Incluye letras y números.' : '');
      confirmation.setCustomValidity(confirmation.value && confirmation.value !== password.value ? 'Las contraseñas no coinciden.' : '');
    }
    const fields = [...panels[index].querySelectorAll('input,select,textarea')];
    const invalid = fields.find(field => !field.checkValidity());
    if (invalid) {
      show(index);
      error.textContent = invalid.type === 'file' ? 'Selecciona entre una y seis fotografías JPG o PNG, con máximo 10 MB en total.' : 'Revisa el campo indicado antes de continuar.';
      invalid.focus();
      invalid.reportValidity();
      return false;
    }
    return true;
  };
  next.addEventListener('click', () => { if (validate(current)) show(current + 1, true); });
  back.addEventListener('click', () => show(current - 1, true));
  form.addEventListener('submit', event => {
    for (let i = 0; i < panels.length; i += 1) {
      if (!validate(i)) { event.preventDefault(); return; }
    }
  });
  form.addEventListener('keydown', event => {
    if (event.key === 'Enter' && event.target.tagName === 'INPUT' && current < panels.length - 1) {
      event.preventDefault();
      if (validate(current)) show(current + 1, true);
    }
  });
  form.addEventListener('input', event => {
    if (event.target.type !== 'file') event.target.setCustomValidity('');
    error.textContent = '';
  });
  show(0);
});

document.querySelectorAll('[data-report-form]').forEach(form => {
  const input = form.querySelector('[data-files]');
  const zone = form.querySelector('[data-dropzone]');
  const previews = form.querySelector('[data-previews]');
  const error = form.querySelector('[data-form-error]');
  let files = [];
  let objectURLs = [];
  const update = () => {
    objectURLs.forEach(url => URL.revokeObjectURL(url));
    objectURLs = [];
    previews.replaceChildren();
    const transfer = new DataTransfer();
    files.forEach((file, index) => {
      transfer.items.add(file);
      const card = document.createElement('div');
      card.className = 'file-preview';
      const image = document.createElement('img');
      const objectURL = URL.createObjectURL(file);
      objectURLs.push(objectURL);
      image.src = objectURL;
      image.alt = `Vista previa de ${file.name}`;
      const label = document.createElement('span');
      label.textContent = `${file.name} · ${(file.size / 1024 / 1024).toFixed(1)} MB`;
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.textContent = '×';
      remove.setAttribute('aria-label', `Quitar ${file.name}`);
      remove.addEventListener('click', () => { files.splice(index, 1); update(); });
      card.append(image, label, remove);
      previews.append(card);
    });
    input.files = transfer.files;
    input.setCustomValidity('');
  };
  const select = incoming => {
    const combined = [...files];
    for (const file of incoming) {
      if (!['image/jpeg', 'image/png'].includes(file.type)) {
        error.textContent = 'Selecciona únicamente fotografías JPG o PNG.';
        update(); return;
      }
      if (!combined.some(item => item.name === file.name && item.size === file.size && item.lastModified === file.lastModified)) combined.push(file);
    }
    if (combined.length > 6 || combined.reduce((size, file) => size + file.size, 0) > 10 * 1024 * 1024) {
      error.textContent = 'Puedes adjuntar máximo 6 fotografías y 10 MB en total.';
      update(); return;
    }
    files = combined;
    error.textContent = '';
    update();
  };
  input.addEventListener('change', () => select([...input.files]));
  ['dragenter', 'dragover'].forEach(type => zone.addEventListener(type, event => {
    event.preventDefault(); zone.classList.add('drag-over');
  }));
  ['dragleave', 'drop'].forEach(type => zone.addEventListener(type, event => {
    event.preventDefault(); zone.classList.remove('drag-over');
  }));
  zone.addEventListener('drop', event => select([...event.dataTransfer.files]));
  window.addEventListener('pagehide', () => objectURLs.forEach(url => URL.revokeObjectURL(url)));
});

document.querySelectorAll('[data-location]').forEach(button => {
  button.addEventListener('click', () => {
    const message = document.querySelector('[data-location-message]');
    if (!navigator.geolocation) { message.textContent = 'Tu navegador no permite obtener la ubicación. Escríbela en el campo.'; return; }
    button.disabled = true;
    message.textContent = 'Buscando tu ubicación. Autoriza el permiso en el navegador.';
    navigator.geolocation.getCurrentPosition(position => {
      document.getElementById('ubicacion').value = `${position.coords.latitude.toFixed(6)}, ${position.coords.longitude.toFixed(6)}`;
      message.textContent = 'Coordenadas incorporadas. Verifica que correspondan al cultivo.';
      button.disabled = false;
    }, () => {
      message.textContent = 'No fue posible obtener tu ubicación. Puedes escribir una dirección o referencia rural.';
      button.disabled = false;
    }, { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 });
  });
});

const sidebar = document.getElementById('navegacion');
const navToggle = document.querySelector('[data-open-nav]');
const shade = document.querySelector('.sidebar-shade');
if (sidebar && navToggle) {
  const close = () => { sidebar.classList.remove('is-open'); shade.classList.remove('is-open'); navToggle.setAttribute('aria-expanded', 'false'); navToggle.focus(); };
  navToggle.addEventListener('click', () => {
    sidebar.classList.add('is-open'); shade.classList.add('is-open'); navToggle.setAttribute('aria-expanded', 'true');
    sidebar.querySelector('[data-close-nav]').focus();
  });
  document.querySelectorAll('[data-close-nav]').forEach(button => button.addEventListener('click', close));
  sidebar.addEventListener('keydown', event => {
    if (event.key === 'Escape') close();
    if (event.key === 'Tab' && sidebar.classList.contains('is-open')) {
      const focusable = [...sidebar.querySelectorAll('a,button')].filter(item => !item.hidden && item.getClientRects().length);
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
}
const publicMenu = document.querySelector('[data-public-menu]');
if (publicMenu) publicMenu.addEventListener('click', () => {
  const expanded = document.querySelector('.public-header nav').classList.toggle('is-open');
  publicMenu.setAttribute('aria-expanded', String(expanded));
  publicMenu.setAttribute('aria-label', expanded ? 'Cerrar menú' : 'Abrir menú');
});

const dialog = document.getElementById('confirmacion');
let pendingForm = null;
const confirmed = new WeakSet();
document.querySelectorAll('[data-confirm]').forEach(form => {
  form.addEventListener('submit', event => {
    if (confirmed.has(form)) return;
    event.preventDefault();
    if (typeof dialog.showModal !== 'function') {
      if (window.confirm(form.dataset.confirm)) { confirmed.add(form); form.requestSubmit(); }
      return;
    }
    pendingForm = form;
    dialog.querySelector('[data-confirm-text]').textContent = form.dataset.confirm;
    dialog.showModal();
  });
});
document.querySelector('[data-cancel-confirm]').addEventListener('click', () => { dialog.close(); pendingForm = null; });
document.querySelector('[data-accept-confirm]').addEventListener('click', () => {
  if (pendingForm) { const form = pendingForm; confirmed.add(form); dialog.close(); pendingForm = null; form.requestSubmit(); }
});
document.querySelectorAll('form[data-loading],form[data-wizard],form[data-confirm]').forEach(form => {
  form.addEventListener('submit', event => {
    if (event.defaultPrevented) return;
    form.querySelectorAll('button[type="submit"],button:not([type])').forEach(button => { button.disabled = true; button.classList.add('is-loading'); });
  });
});
window.addEventListener('pageshow', () => document.querySelectorAll('.is-loading').forEach(button => { button.disabled = false; button.classList.remove('is-loading'); }));

if (!reduceMotion) {
  document.querySelectorAll('[data-count]').forEach(element => {
    const target = Number(element.dataset.count);
    if (!target) return;
    let start;
    const frame = time => {
      start ??= time;
      const progress = Math.min((time - start) / 650, 1);
      element.textContent = String(Math.round(target * (1 - Math.pow(1 - progress, 3))));
      if (progress < 1) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); }
    }), { threshold: 0.1 });
    document.querySelectorAll('.reveal').forEach(element => {
      if (element.getBoundingClientRect().top > window.innerHeight) { element.classList.add('will-reveal'); observer.observe(element); }
    });
  }
}
