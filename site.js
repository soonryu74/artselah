/* Artselah — 메뉴, 작품 크게 보기, 문의 메일 */
(() => {
  const en = document.documentElement.lang === 'en';
  const $ = id => document.getElementById(id);

  /* 상단 메뉴 */
  const nav = $('nav'), menu = $('menu'), links = $('links');
  addEventListener('scroll', () => nav.classList.toggle('solid', scrollY > 10), { passive: true });
  menu.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    menu.setAttribute('aria-expanded', open);
  });
  links.addEventListener('click', e => {
    if (e.target.closest('a')) { links.classList.remove('open'); menu.setAttribute('aria-expanded', false); }
  });

  /* 작품 크게 보기 */
  const lb = $('lightbox'), works = window.WORKS || [];
  let cur = 0;
  const showWork = i => {
    cur = (i + works.length) % works.length;
    const w = works[cur];
    lb.classList.remove('photo');
    $('lb-img').src = w.img;
    $('lb-img').alt = w.title;
    $('lb-title').textContent = w.title;
    $('lb-meta').textContent = w.meta;
    $('lb-mat').textContent = w.mat;
    $('lb-desc').textContent = w.desc;
    if (!lb.open) lb.showModal();
  };
  const showPhoto = (src, cap) => {
    lb.classList.add('photo');
    $('lb-img').src = src;
    $('lb-img').alt = cap;
    $('lb-cap').textContent = cap;
    if (!lb.open) lb.showModal();
  };
  document.querySelectorAll('[data-work]').forEach(b =>
    b.addEventListener('click', () => showWork(+b.dataset.work)));
  document.querySelectorAll('.view').forEach(b =>
    b.addEventListener('click', () => showPhoto(b.dataset.src, b.dataset.cap)));
  $('lb-close').addEventListener('click', () => lb.close());
  $('lb-prev').addEventListener('click', () => showWork(cur - 1));
  $('lb-next').addEventListener('click', () => showWork(cur + 1));
  lb.addEventListener('click', e => { if (e.target === lb) lb.close(); });
  lb.addEventListener('keydown', e => {
    if (lb.classList.contains('photo')) return;
    if (e.key === 'ArrowLeft') showWork(cur - 1);
    if (e.key === 'ArrowRight') showWork(cur + 1);
  });

  /* 문의 양식 */
  const form = $('inquiry');
  const goContact = (kind, msg) => {
    if (kind) form.kind.value = kind;
    if (msg && !form.msg.value) form.msg.value = msg;
    $('contact').scrollIntoView({ behavior: 'smooth' });
    setTimeout(() => form.name.focus({ preventScroll: true }), 700);
  };
  document.querySelectorAll('[data-ask]').forEach(b =>
    b.addEventListener('click', () => goContact(b.dataset.ask)));
  $('lb-ask').addEventListener('click', () => {
    const w = works[cur];
    lb.close();
    goContact(form.kind.options[0].value,
      en ? `I would like to know more about ${w.ask || 'this work'}.`
         : `${w.ask || '이 작품'}에 대해 알고 싶습니다.`);
  });

  const MAIL = 'estherp@artselah.com';
  const toast = $('toast');
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const f = form;
    const subject = en ? `[Artselah Enquiry] ${f.kind.value} — ${f.name.value}`
                       : `[아트셀라 문의] ${f.kind.value} — ${f.name.value}`;
    const body = en
      ? `Enquiry: ${f.kind.value}\nName: ${f.name.value}\nContact: ${f.reach.value}\n\n${f.msg.value}`
      : `문의 분야: ${f.kind.value}\n성함: ${f.name.value}\n연락처: ${f.reach.value}\n\n${f.msg.value}`;
    try { await navigator.clipboard.writeText(body); } catch (_) {}
    toast.textContent = en ? 'Opening your mail app…' : '메일 앱이 열립니다. 보내기만 누르시면 됩니다.';
    toast.classList.add('on'); setTimeout(() => toast.classList.remove('on'), 3500);
    location.href = `mailto:${MAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });

  /* 스크롤하면 부드럽게 나타나기 */
  const io = 'IntersectionObserver' in window && new IntersectionObserver(es => es.forEach(x => {
    if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); }
  }), { threshold: .08 });
  document.querySelectorAll('.grid li, .views li, .sec-head, .artist-grid, .ex-grid, .about-grid, .svc-card').forEach(el => {
    if (!io) return;
    el.classList.add('rv'); io.observe(el);
  });
})();
