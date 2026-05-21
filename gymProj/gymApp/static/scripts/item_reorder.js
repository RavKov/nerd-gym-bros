const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

const createItemReorderSortable = (ulContainerId, itemSelector, handleSelector, url) => {
    const el = document.getElementById(ulContainerId);

    return Sortable.create(el, {
        animation: 150,
        handle: handleSelector,
        onEnd: async () => {
            elements = [...el.querySelectorAll(itemSelector)];
            let i = 1;
            elements.forEach(element => {
                element.setAttribute('data-order', i);
                i++;
            });

            await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify(elements.map(el => ({
                    id: el.getAttribute("data-id"),
                    order: el.getAttribute("data-order"),
                }))),
            });

        }
    });
}