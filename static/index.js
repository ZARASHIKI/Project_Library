//User logout
function logout() {
    $.cookie('mytoken');
    $.removeCookie('mytoken',{path: '/', expires: 1, sameSite: 'None', secure: true });
    alert('You have been logged out!');
    window.location.href = '/';
}

// Tambah Buku
function tambahBuku() {
    let judul = $('#judul').val()
    let penulis = $('#penulis').val()
    let genre = $('#genre').val()
    let cover = $('#cover')[0].files[0]
    let link = $('#link').val()
    let deskripsi = $('#deskripsi').val()
    let form_data = new FormData();
    form_data.append("judul_give",judul)
    form_data.append("penulis_give",penulis)
    form_data.append("genre_give",genre)
    form_data.append("cover_give",cover)
    form_data.append("link_give",link)
    form_data.append("deskripsi_give",deskripsi)

$.ajax({
    type:'POST',
    url:'/tambah_buku/save',
    data:form_data,
    cache: false,
    contentType: false,
    processData: false,
    success: function(response){
        if (response.result === 'success') {
            alert(response.msg)
        }
    }
})
}
