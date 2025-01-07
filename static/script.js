// Change Navbar Background on Scroll
document.addEventListener('scroll', function () {
  const navbar = document.querySelector('.navbar');
  if (window.scrollY > 200) {
    navbar.classList.remove('scrolled');
  } else {
    navbar.classList.add('scrolled');
  }

  document.getElementById('year').textContent = new Date().getFullYear();
});
