var swiper = new Swiper(".mySwiper", {
    cssMode: true,
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    pagination: {
      el: ".swiper-pagination",
    },
    mousewheel: true,
    keyboard: true,
  });
  
  var articles = document.querySelectorAll('.posts .post');
  var numArticlesToShow = 9;
  var numArticlesShown = 0;
  var isLoading = false;
  
  function showMoreArticles() {
    var i;
    for (i = numArticlesShown; i < numArticlesShown + numArticlesToShow; i++) {
      if (articles[i]) {
        articles[i].style.display = 'block';
      }
    }
    numArticlesShown += numArticlesToShow;
    if (numArticlesShown >= articles.length) {
      window.removeEventListener('scroll', handleScroll);
    }
    isLoading = false;
  }
  
  function handleScroll() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var scrollHeight = document.documentElement.scrollHeight;
    var clientHeight = document.documentElement.clientHeight;
  
    if (scrollTop + clientHeight >= scrollHeight && !isLoading) {
      isLoading = true;
      document.getElementById('spinner').style.display = 'block';
      setTimeout(function() {
        document.getElementById('spinner').style.display = 'none';
        showMoreArticles();
      }, 1000);
    }
  }
  
  window.addEventListener('scroll', handleScroll);
  
  document.getElementById('spinner').style.display = 'none';
  showMoreArticles();
  