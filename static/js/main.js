const navItems = document.querySelector(".nav__items");
const openNavBtn = document.querySelector("#open__nav-btn");
const closeNavBtn = document.querySelector("#close__nav-btn");

const openNav = () => {
  navItems.style.display = "flex";
  openNavBtn.style.display = "none";
  closeNavBtn.style.display = "inline-block";
};

const closeNav = () => {
  navItems.style.display = "none";
  openNavBtn.style.display = "inline-block";
  closeNavBtn.style.display = "none";
};

openNavBtn.addEventListener("click", openNav);
closeNavBtn.addEventListener("click", closeNav);

// ── Toast auto-dismiss ──
(function () {
  function dismissToast(toast) {
    toast.classList.add('toast--hiding');
    toast.addEventListener('transitionend', function () { toast.remove(); }, { once: true });
  }
  document.querySelectorAll('.toast').forEach(function (toast) {
    toast.querySelector('.toast__close').addEventListener('click', function () {
      dismissToast(toast);
    });
    setTimeout(function () { dismissToast(toast); }, 4500);
  });
})();

const comments = document.querySelector(".allcomments__block");
const show_hide__btn = document.querySelector(".comment__btn");

if (comments && show_hide__btn) {
  const show_hide_comments = () => {
    if (comments.style.display == "block") {
      comments.style.display = "none";
      show_hide__btn.innerHTML =
        'Show Comments <i class="uil uil-comment-download"></i>';
    } else {
      comments.style.display = "block";
      show_hide__btn.innerHTML =
        'Hide Comments <i class="uil uil-corner-right-down"></i>';
    }
  };
  show_hide__btn.addEventListener("click", show_hide_comments);
}















