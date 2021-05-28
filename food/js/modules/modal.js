
function openModal (modalSelector, modalTimerId) {
    const modal = document.querySelector(modalSelector);

    modal.classList.add('show');
    modal.classList.remove('hide');
    document.body.style.overflow = 'hidden';

    console.log(modalTimerId);
    if (modalTimerId) {
        clearInterval(modalTimerId);
    }
}
function closeModal (modalSelector) {
    const modal = document.querySelector(modalSelector);
    modal.classList.remove('show');
    modal.classList.add('hide');
    document.body.style.overflow = '';
}

function modal(triggerSelector, modalSelector, modalTimerId) {
    const modalTrigger = document.querySelectorAll(triggerSelector),
          modal = document.querySelector(modalSelector);

    modalTrigger.forEach(btn => {
        btn.addEventListener('click', () =>  openModal(modalSelector, modalTimerId));

    });

    modal.addEventListener('click', (event) => {
        if (event.target === modal || event.target.getAttribute('data-close') == "") {
           closeModal(modalSelector);
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.code === 'Escape' && modal.classList.contains('show')) {
            closeModal(modalSelector);
        }
    });

    function showModalByScroll () {
        if (document.documentElement.scrollTop + document.documentElement.clientHeight == document.documentElement.scrollHeight) {
            openModal(modalSelector, modalTimerId);
            document.removeEventListener('scroll', showModalByScroll);
        }
    }

    document.addEventListener('scroll', showModalByScroll);

}

export default modal;
export {openModal};
export {closeModal};