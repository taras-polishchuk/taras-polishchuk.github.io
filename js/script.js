//promo btn logics
const links = document.querySelectorAll('.promo__link');

links.forEach(link => {
    link.addEventListener('mouseover', (e) => {
        links.forEach(item => {
            item.classList.remove('btn_active');
        });
        e.target.classList.add('btn_active');
    });
});

//menu showing
const menu = document.querySelector('.menu'),
      hamburger = document.querySelector('.hamburger'),
      closeBtn = document.querySelector('.menu__close'),
      overlay = document.querySelector('.menu__overlay'),
      menuLinks = document.querySelectorAll('.menu__link a'),
      menuSocialLinks = document.querySelectorAll('.menu__social a');

  //show
hamburger.addEventListener('click', (e) => {
    e.preventDefault();
    menu.classList.toggle('active');
});

  //close
function closeMenu(elem) {
    elem.addEventListener('click', (e) =>{
        // e.preventDefault();
        menu.classList.toggle('active');
    });
}

menuLinks.forEach(link => {
   closeMenu(link);
});

menuSocialLinks.forEach(link => {
    closeMenu(link);
}); 

closeMenu(closeBtn);
closeMenu(overlay);

//showing progress bar percent indication
const percentItems = document.querySelectorAll('.progress__item_percent'),
      indicationLines = document.querySelectorAll('.progress__item_line-progress');

percentItems.forEach((item, i) => {
    indicationLines[i].style.width = item.textContent;
});

//portfolio efect with css-filter
const linkItems = document.querySelectorAll('.portfolio__item'),
      imgs = document.querySelectorAll('.portfolio__item img');

linkItems.forEach((link, i) => {
    link.addEventListener('mouseenter', (e) =>{
        e.preventDefault();
        imgs.forEach(img => {
            img.style.filter = 'grayscale(80%)';
        });
        imgs[i].style.filter = 'grayscale(0)';
    });
    link.addEventListener('mouseleave', (e) =>{
        e.preventDefault();
        imgs.forEach(img => {
            img.style.filter = 'grayscale(0)';
        });
        imgs[i].style.filter = 'grayscale(0)';
    });
});

//mailer. send mail from portfolio to my adress with php plugin and jquery
$('form').submit(function(e) {
    e.preventDefault();
    $.ajax({
        type:"POST",
        url: "mailer/smart.php",
        data: $(this).serialize()
    }).done(function() {
        $(this).find("input").val("");

        $('.contacts__triggers button').text('Отправлено');

        $('form').trigger('reset');
    });
    return false;
});

$(window).scroll(() => {
    if ($(this).scrollTop() > 1600) {
        $('.pageup').fadeIn();
    } else {
        $('.pageup').fadeOut();
    }
});

$("a[href^='#up']").click(function(){
    const _href = $(this).attr("href");
    $("html, body").animate({scrollTop: $(_href).offset().top+"px"});
    return false;
});