//User logout
function logout() {
    $.cookie('mytoken');
    $.removeCookie('mytoken', { path: '/', expires: 1, sameSite: 'None', secure: true });
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
    if (!judul || !penulis || !genre || !cover || !link || !deskripsi) {
        alert("Semua kolom harus diisi. Silakan lengkapi formulir.");
    } else {
        let form_data = new FormData();
        form_data.append("judul_give", judul)
        form_data.append("penulis_give", penulis)
        form_data.append("genre_give", genre)
        form_data.append("cover_give", cover)
        form_data.append("link_give", link)
        form_data.append("deskripsi_give", deskripsi)

        $.ajax({
            type: 'POST',
            url: '/tambah_buku/save',
            data: form_data,
            cache: false,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.result === 'success') {
                    alert(response.msg)
                    window.location.reload()
                }
            }
        })
    }
}

// Edit Buku
function edit_buku() {
    let judul = $('#judul').val()
    let penulis = $('#penulis').val()
    let genre = $('#genre').val()
    let cover = $('#cover')[0].files[0]
    let link = $('#link').val()
    let deskripsi = $('#deskripsi').val()
    if (!judul || !penulis || !genre || !cover || !link || !deskripsi) {
        alert("Semua kolom harus diisi. Silakan lengkapi formulir.");
    } else {
        let form_data = new FormData();
        form_data.append("judul_give", judul)
        form_data.append("penulis_give", penulis)
        form_data.append("genre_give", genre)
        form_data.append("cover_give", cover)
        form_data.append("link_give", link)
        form_data.append("deskripsi_give", deskripsi)

        $.ajax({
            type: 'POST',
            url: '/Edit_buku/save',
            data: form_data,
            cache: false,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.result === 'success') {
                    alert(response.msg)
                    window.location.reload()
                }
            }
        })
    }

}
// Delete Buku
function delete_buku(judul) {
    let judul1 = judul
    console.log(judul1)
    $.ajax({
        type: 'POST',
        url: '/delete_buku/save',
        data: {
            judul_give: judul1
        },
        success: function (response) {
            if (response.result === 'success') {
                alert(response.msg)
                window.location.href = "/collection"
            }
        }
    })
}


// toogle bookmark
function bookmark(id, type, cover, detail, judul) {
    let mark = $(".bookmark-btn")
    if (mark.attr("style") && mark.css("color") === "rgb(255, 255, 255)") {
        $.ajax({
            type: "POST",
            url: "/bookmark/add",
            data: {
                id_give: id,
                type_give: type,
                cover_give: cover,
                detail_give: detail,
                judul_give: judul,
                action_give: 'Bookmark'
            },
            success: function (response) {
                window.location.reload()
                mark.css("color", "red")
            },
        });

    }
    else {
        $.ajax({
            type: "POST",
            url: "/bookmark/add",
            data: {
                id_give: id,
                type_give: type,
                cover_give: cover,
                detail_give: detail,
                judul_give: judul,
                action_give: 'unbook'
            },
            success: function (response) {
                window.location.reload()
                mark.css("color", "white")
            },
        });
    }
}

// get bookmark

function loadboomark(page) {
    $.ajax({
        type: "GET",
        url: `/bookmark?page=${page}`,
        success: function (response) {
            cekbookmark()
            $("#current-page").text(page);
            $("#total-pages").text(2);
        },
    });
}

function cekbookmark(username, judul) {
    if (username === undefined) {
        username = "";
    }
    $("#bookmarkcard").empty();
    let hasMatchingBookmark = false; 
    $.ajax({
        type: "GET",
        url: `/bookmark/cek?username_give=${username}`,
        data: {},
        success: function (response) {
            if (response["result"] === "success") {
                let bookmark = response["bookmark"];
                for (let i = 0; i < bookmark.length; i++) {
                    let bookmark1 = bookmark[i];
                    let judul1 = bookmark1['judul'];
                    if (judul1 === judul) {
                        hasMatchingBookmark = true;
                    }
                }
                if (hasMatchingBookmark) {
                    $("#bookmarkicon").attr("style", "color: red");
                } else {
                    $("#bookmarkicon").attr("style", "color: white");
                }
            }
        }
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

function loadPage(page) {
    $.ajax({
        type: "GET",
        url: `/collection?page=${page}`,
        success: function (response) {
            $("#current-page").text(page);
            $("#total-pages").text(2);
        },
    });
}