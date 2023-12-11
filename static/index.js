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

// toogle bookmark
function bookmark(id,type,cover,detail) {
    let mark = $(".bookmark-btn")
    if(!mark.attr("style")){
        $.ajax({
            type:"POST",
            url:"/bookmark/add",
            data:{
            id_give:id,
            type_give:type,
            cover_give:cover,
            detail_give:detail,
            action_give:'Bookmark'
            },
            success: function (response){
                alert("Success add bookmark")
                mark.css("color","black")            },
        });
        
    }
    else{
        $.ajax({
            type:"POST",
            url:"/bookmark/add",
            data:{
            id_give:id,
            type_give:type,
            cover_give:cover,
            detail_give:detail,
            action_give:'unbook'
            },
            success: function (response){
                alert("Delete bookmark success")
                mark.css("color","")
            },
        });
    }
}

// get bookmark
function getbookmark(username) {
    if (username == undefined) {
        username = "";
    }
    $("#bookmarkcard").empty();
    $.ajax({
        type: "GET",
        url: `/bookmark/get?username_give=${username}`,
        data: {},
        success: function (response) {
            if (response["result"] === "success") {
                console.log(response)
                let bookmark = response["bookmark"];
                for (let i = 0; i < bookmark.length; i++) {
                    let bookmark1 = bookmark[i];
                    let iconbook = bookmark1['bookmark_me']?"color: black;":"color:;";
                    let temp_html = `
                    <div class="koleksian_image">
                    <a href="${bookmark1['detail']}"><img src="/static/${bookmark1['cover']}" /></a>
                    </div>`
                    let temp_book =`style="${iconbook}"`
                    $("#bookmarkicon").attr("style",iconbook);
                    $("#bookmarkcard").append(temp_html);
                }
            }}
    });
}

// Edit profile
function editprofile() {
        let name = $("#profile_name").val();
        let file = $("#foto")[0].files[0];
        let form_data = new FormData();
        console.log(name)
        form_data.append("file_give", file);
        form_data.append("name_give", name);      
        $.ajax({
          type: "POST",
          url: "/update_profile",
          data: form_data,
          cache: false,
          contentType: false,
          processData: false,
          success: function (response) {
            if (response["result"] === "success") {
              alert(response["msg"]);
              window.location.reload();
            }
          },
        });
}