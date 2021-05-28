	// tiny-slider connections and settings
	const slider = tns({
		"container": ".carousel__inner",
		"nav": true,
		"items": 1,
		"controls": false,
		"responsive": {
			"992": {
			"nav": false,
			"items": 1
			}
		},
		"speed": 400
		});
	
	document.querySelector('.prev').addEventListener('click', () => {
		slider.goTo('prev');
	});
	document.querySelector('.next').addEventListener('click', () => {
		slider.goTo('next');
	}) ;

window.addEventListener('load', () => {
	const tabs = document.querySelectorAll('.catalog__tab'),
		catalogLinks = document.querySelectorAll('.catalog-item__link'),
		contents = document.querySelectorAll('.catalog-item__content'),
		lists = document.querySelectorAll('.catalog-item__list'),
		catalogBlocks = document.querySelectorAll('.catalog__content');

	//toggle tabs and elements of catalog
	tabs.forEach((tab) => {
		tab.addEventListener('click', (e) => {
			tabs.forEach((item) => {
				item.classList.remove('catalog__tab_active');
			});
			e.currentTarget.classList.add('catalog__tab_active');
			tabs.forEach((item, i) => {
				if (item.classList.contains('catalog__tab_active')) {
					catalogBlocks.forEach(catalog => {
						catalog.classList.remove('catalog__content_active');
					});
					catalogBlocks[i].classList.add('catalog__content_active');
				}
			});
		});
	});

	//show/hide item-card information
	catalogLinks.forEach(link => {
		link.addEventListener('click', (e) => {
			e.preventDefault();
			const parent = e.target.parentNode;
			contents.forEach(content => {
				if(parent === content) {
					content.classList.toggle('catalog-item__content_active');
					e.target.parentNode.nextElementSibling.classList.toggle('catalog-item__list_active');
				}
			});
			lists.forEach(list => {
				if(parent === list) {
					list.classList.toggle('catalog-item__list_active');
					e.target.parentNode.previousElementSibling.classList.toggle('catalog-item__content_active');
				}
			});
		});
	});

	//call modals
	const overlay = document.querySelector('.overlay'),
		  closeBtn = document.querySelectorAll('.modal__close'),
		  consultationModal = document.querySelector('#consultation'),
		  orderModal = document.querySelector('#order'),
		  thanksModal = document.querySelector('#thanks');


	showSelectedModal('[data-modal=consultation]', consultationModal);
	showSelectedModal('.button_catalog', orderModal);



	closeBtn.forEach(btn => {
		btn.addEventListener('click', () => {
			removeModal();
		});
	});

	document.addEventListener('click', (e) => {
		if (e.target === overlay) {
			removeModal();
		}
	});


	function showModal(modalType) { //make visible
		modalType.classList.toggle('modal_active');
	}

	function showSelectedModal(buttonSelector, modalType) { //for selected button respons relevant modal
		document.querySelectorAll(buttonSelector).forEach((button, i) => {
			button.addEventListener('click', (e) => {
				e.preventDefault();
				overlay.classList.toggle('overlay_active');
				if (modalType == orderModal) { //add item relevant text from some product card  to modal subtitle 
					document.querySelector('#order .modal__descr').textContent = document.querySelectorAll('.catalog-item__subtitle')[i].textContent;
				}
				showModal(modalType);
				document.querySelector('body').classList.toggle('scroll-hidden');
			});
		});
	}

	function removeModal() {
		overlay.classList.remove('overlay_active');
		removeActive(consultationModal);
		removeActive(orderModal);
		removeActive(thanksModal);
		document.querySelector('body').classList.toggle('scroll-hidden');
	}

	function removeActive(someModal) {
		someModal.classList.remove('modal_active');
	}


	//form validation with jQuery and jQuery validation plugin
	function validateForms(form) {
		$(form).validate({
			messages: {
				name: "Пожалуйста, введите свое имя",
				phone: "Пожалуйста, введите свой номер телефона",
				email: {
					required: "Пожалуйста, введите свою почту",
					email: "Неправильно введен адрес почты"
				}
			}
		});
	}

	validateForms('#consultation-form');
	validateForms('#consultation form');
	validateForms('#order form');

	//phone mask for all phone inputs on the page with jquery masked input plugin
	$('input[name="phone"]').mask("+(999) 999-9999");

	//sending data from form to email
	$('form').submit(function(e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: "mailer/smart.php",
            data: $(this).serialize()
        }).done(function() {
            $(this).find("input").val("");
            removeActive(orderModal);
			removeActive(consultationModal);
			overlay.classList.toggle('overlay_active');
            showModal(thanksModal);
            $('form').trigger('reset');
        });
        return false;
    });

	//Smooth scroll & pageup
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

	//init WOW 
	new WOW().init();

});