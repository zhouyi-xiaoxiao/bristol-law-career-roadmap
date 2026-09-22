(() => {
  const navLinks = [...document.querySelectorAll('.chapter-nav a')];
  const sections = [...document.querySelectorAll('main > section[id]')];
  let pending = false;
  const mark = () => {
    let current = sections[0]?.id;
    for (const section of sections) if (section.getBoundingClientRect().top <= 145) current = section.id;
    navLinks.forEach(link => {
      const active = link.hash === '#' + current;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');
    });
    pending = false;
  };
  window.addEventListener('scroll', () => { if (!pending) { pending = true; requestAnimationFrame(mark); } }, {passive: true});
  mark();
  document.querySelectorAll('.mobile-nav a').forEach(link => link.addEventListener('click', () => {
    document.querySelector('.mobile-nav').removeAttribute('open');
  }));
  document.addEventListener('keydown', event => { if (event.key === 'Escape') document.querySelector('.mobile-nav')?.removeAttribute('open'); });
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const text = document.getElementById(button.dataset.copy).textContent;
    try {
      await navigator.clipboard.writeText(text);
      button.textContent = '已复制';
      document.getElementById('copy-status').textContent = '已复制。请按真实情况替换括号内容。';
      setTimeout(() => { button.textContent = '复制文本'; }, 2200);
    } catch {
      const range = document.createRange(); range.selectNodeContents(document.getElementById(button.dataset.copy));
      const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
      button.textContent = '已选中，请手动复制';
      document.getElementById('copy-status').textContent = '请手动复制选中的文字。';
    }
  }));
  document.querySelectorAll('[data-open-section]').forEach(link => link.addEventListener('click', () => {
    const target = document.querySelector(link.hash); if (target?.tagName === 'DETAILS') target.open = true;
  }));
})();
