

window.onload = () => {
    let info = document.getElementById('info');
    const params = new URLSearchParams(location.search);

    info.innerText = params.get("info") ?? ""

}
