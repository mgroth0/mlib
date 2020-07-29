var links = document.getElementsByTagName('a')
for (link of links) {
    if (link.getAttribute("href") != null && link.getAttribute("href").startsWith("#")) {
        link.onclick = (e) => {
            link.scrollIntoView()
            return false
        }
    }
}