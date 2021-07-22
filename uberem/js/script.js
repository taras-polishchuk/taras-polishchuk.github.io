//toggle switcher 
const switcherBtns = document.querySelectorAll('.header__switcher-item');

    switcherBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            switcherBtns.forEach(item => {
                item.classList.toggle('header__switcher-active');
            });
        });
    });

//promo__btn sizing on scroll and white background for fixed meny
const btn = document.querySelector('.promo__btn'),
      header = document.querySelector('.header'),
      area = document.querySelector('.promo__area'),
      btnText = document.querySelector('.promo__btn_text'),
      btnBorder = document.querySelector('.promo__btn_border');

document.addEventListener('scroll', () => {
    const scroll = document.documentElement.scrollTop;

    if(scroll < 3) {
        btn.style.left = '50%';
        btn.style.top = '80%';
        btn.classList.remove('promo__btn_small');
        header.classList.remove('header_white-bg');
    } else {
        btn.style.left = '50%';
        btn.style.top = '90%';
        btn.classList.add('promo__btn_small');
        header.classList.add('header_white-bg');
    }
});

btn.addEventListener('mouseover', () => {
    btnBorder.classList.add('promo__btn_border_bigger');
});

btn.addEventListener('mousemove', (e) => {
    const left = e.clientX;
    const top = e.clientY;

    if(
            left < ((document.documentElement.clientWidth / 2) + 150) && 
            left > ((document.documentElement.clientWidth / 2) - 150) &&
            top > (document.documentElement.clientHeight  - 300)
        ) {
        btn.classList.remove('promo__btn_small');
        btn.style.left = left + 'px';
        btn.style.top = (top - 100) + 'px';
    }
});

btn.addEventListener('mouseout', (e) => {
    btn.classList.add('promo__btn_small');
    btnBorder.classList.remove('promo__btn_border_bigger');
    btn.style.left = '50%';
    btn.style.top = '90%';
});


//cards animation
const cards = document.querySelectorAll('.advantages__item');

function intervalShow(arrWithItems) {
    let index = -1;
     
    const timer = setInterval(function(){
      // End the timer when at the end of the array 
        if (++index >= arrWithItems.length) {
            clearInterval(timer);
            return;
        } else {
            let item = arrWithItems[index];
            item.classList.add('advantages__item_active');
        } 
        
    }, 100);
}

function removeActiveClass(arr) {
    arr.forEach(item => {
        item.classList.remove('advantages__item_active');
    });
}


//tabs
const tabsParent = document.querySelector('.side-panel__list'),
      tabs = document.querySelectorAll('.side-panel__list_item'),
      tabsContent = document.querySelectorAll('.tabs__image'),
      tabsWrapper = document.querySelector('.tabs__wrapper'),
      sidePanelWrapper = document.querySelector('.side-panel');


//activation for tabs
function tabsActivation() {
    sidePanelWrapper.classList.remove('side-panel_hidden');
    tabsWrapper.classList.remove('tabs__wrapper_unactive');
    getActiveTab();
}

function tabsUnactivation() {
    sidePanelWrapper.classList.add('side-panel_hidden');
    tabsWrapper.classList.add('tabs__wrapper_unactive');
    markersOffOnActiveTab();

}

btn.addEventListener('click', () => {
    sidePanelWrapper.classList.toggle('side-panel_hidden');
    tabsWrapper.classList.toggle('tabs__wrapper_unactive');
    getActiveTab();
});

document.addEventListener('scroll', () => {
    const scroll = document.documentElement.scrollTop;

    if(scroll >= 1200) {
        tabsActivation();
        header.classList.add('header_hidden');
        btn.classList.add('promo__btn_hidden');
        btn.classList.remove('promo__btn_small');
        btnBorder.classList.add('promo__btn_border_hidden');
    } else {
        tabsUnactivation();
        header.classList.remove('header_hidden');
        btn.classList.remove('promo__btn_small');
        btn.classList.remove('promo__btn_hidden');
        btn.classList.add('promo__btn_small');
        btnBorder.classList.remove('promo__btn_border_hidden');
        removeActives(labels, 'tabs__image_marker-text_active');
        removeActives(markerBtns, 'tabs__image_marker-btn_area-active');
        removeActives(btnAreas, 'tabs__image_marker-btn_active');
    }

    //cards activations on scroll
    if(document.documentElement.scrollTop > 300) {
        return;
    } else if(document.documentElement.scrollTop < 250) {
        removeActiveClass(cards);
        return;
    } else if(document.documentElement.scrollTop >= 250) { 
        intervalShow(cards);
        return;
    }
});




function hideTabsContent() {
    tabsContent.forEach(item => {
        item.classList.remove('tabs__image-active');
    });

    tabs.forEach(item => {
        item.classList.remove('side-panel__list_item-active');
    });

}

function showTabContent(i = 0) {
    tabs[i].classList.add('side-panel__list_item-active');
    tabsContent[i].classList.add('tabs__image-active');
}

showTabContent();


tabsParent.addEventListener('click', (event) => {
    const target = event.target;

    if (target && target.classList.contains('side-panel__list_item')) {

        tabs.forEach((item, i) => {
            if (item == target) {
                hideTabsContent();
                showTabContent(i);
                getAllMarkers(tabsContent[i]);
                markersOffOnActiveTab();
                removeActives(labels, 'tabs__image_marker-text_active');
                removeActives(markerBtns, 'tabs__image_marker-btn_area-active');
                removeActives(btnAreas, 'tabs__image_marker-btn_active');
            }
        });
    }
});

tabsParent.addEventListener('mouseover', (event) => {
    const target = event.target;

    if (target && target.classList.contains('side-panel__list_item')) {

        tabs.forEach((item, i) => {
            if (item == target) {
                tabsContent[i].classList.add('tabs__image-hovered');
                markersOffOnAllTabs();
            }
        });
    }
});

tabsParent.addEventListener('mouseout', (event) => {
    const target = event.target;

    if (target && target.classList.contains('side-panel__list_item')) {

        tabs.forEach((item, i) => {
            if (item == target) {
                tabsContent[i].classList.remove('tabs__image-hovered');
            }
        });
    }
});

function getAllMarkers(someTab) {
    const markers = someTab.querySelectorAll('.tabs__image_marker');

    
    markers.forEach(item  => { 
        setTimeout(function() {
            item.classList.add('tabs__image_marker-active');
        }, 1000);  
        
    });
    
}

function removeMarkers(someTab) {
    const markers = someTab.querySelectorAll('.tabs__image_marker');

    markers.forEach(item  => {
        item.classList.remove('tabs__image_marker-active');
    });
    
}


function getActiveTab() {
    tabsContent.forEach(item => {
        if (item.classList.contains('tabs__image-active')) {
            getAllMarkers(item);
        }
    });
}
function markersOffOnActiveTab() {
    tabsContent.forEach(item => {
        if (item.classList.contains('tabs__image-active')) {
            removeMarkers(item);
        } 
    });
}

function markersOffOnAllTabs() {
    tabsContent.forEach(item => {
        if (item.classList.contains('tabs__image-active')) {
            getAllMarkers(item);
        } else {
            removeMarkers(item);
        }
    });
}


//functionslity on markers 
const markerBtns = document.querySelectorAll('.tabs__image_marker-btn_area'),
      labels = document.querySelectorAll('.tabs__image_marker-text'),
      btnAreas = document.querySelectorAll('.tabs__image_marker-btn');

markerBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        const target = e.currentTarget;
        markerBtns.forEach((item, i) => {
            if (item == target) {
                labels[i].classList.toggle('tabs__image_marker-text_active');
                item.classList.toggle('tabs__image_marker-btn_area-active');
                btnAreas[i].classList.toggle('tabs__image_marker-btn_active');
            }
        });
    });
});

function removeActives(items, activeClass) {
    items.forEach(item => {
        item.classList.remove(activeClass);
    });
    
}

      