window.onload = function() {
    var btns = document.getElementsByClassName('btn');
    for(var i = 0; i < btns.length; i++) {
        var btn = btns[i];
        btn.onclick = function() {
            document.getElementById('loading').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Carregando...'
            document.getElementById('result').innerHTML = ''
            return
        }
    }
}