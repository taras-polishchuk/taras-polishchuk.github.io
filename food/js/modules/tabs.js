function tabs(tabsSelector, tabsContentSelector, tabsParentSelector, activeClass) {
    //Tabs
    const tabs = document.querySelectorAll(tabsSelector),
          tabsContent = document.querySelectorAll(tabsContentSelector),
          tabsParent = document.querySelector(tabsParentSelector);

    function hideTabsContent() {
        tabsContent.forEach(item => {
            item.classList.add('hide');
            item.classList.remove('show', 'fade');
        });

        tabs.forEach(item => {
            item.classList.remove(activeClass);
        });
    }

    function showTabContent(i = 0) {
        tabs[i].classList.add(activeClass);
        tabsContent[i].classList.remove('hide');
        tabsContent[i].classList.add('show', 'fade');
    }

    hideTabsContent();
    showTabContent();

    tabsParent.addEventListener('click', (event) => {
        const target = event.target;

        if (target && target.classList.contains(tabsSelector.slice(1))) {

            tabs.forEach((item, i) => {
                if (item == target) {
                    hideTabsContent();
                    showTabContent(i);
                }
            });
        }
    }); 
}

export default tabs;