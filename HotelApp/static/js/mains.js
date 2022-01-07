function pay() {
   fetch('/api/pay', {
        method: 'post',
        headers: {
            'Context-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        location.href= '/payment';
    })
    .catch(err => {
        location.href = '/payment';
    });
}

function changeActive(id) {
    fetch('/api/changeActive', {
         method: 'post',
         body: JSON.stringify({
            'id': id
        }),
        headers: {
            'Context-Type': 'application/json',
        }
    })
    .then(res => console.log(res))
    .then(data=>{
    alert("Thao tác thành công")
        location.reload()
    })
    .catch(err=>{
    alert("Thao tác thất bại")
        location.reload();
    })
}

function delCart(id) {
   fetch('/api/delCart', {
        method: 'post',
        body: JSON.stringify({
            'id': id
        }),
        headers: {
            'Context-Type': 'application/json'
        }

    })
    .then(data => {
        location.href = '/payment';
    })
    .catch(err => {
        location.href = '/payment';
    });
}

function reg_price(id) {
    fetch('/api/reg_price', {
         method: 'post',
         body: JSON.stringify({
            'id': id
         }),
         headers: {
            'Context-Type': 'application/json',
         }
    })
    .then(data=>{
    alert("Thao tác thành công")
        location.reload()
    })
    .catch(err=>{
    alert("Thao tác thất bại")
        location.reload();
    })
}

function add_comment(roomId) {
    let content = document.getElementById('commentId')
    if ( content !== null) {
        fetch('/api/comments', {
            method: 'post',
            body: JSON.stringify({
                'room_id': roomId,
                'content': content.value
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            if (data.status == 201) {
                let c = data.comment

                let area = document.getElementById('commentArea')

                area.innerHTML = `
                    <div class="row">
                        <div class="col-md-1 col-xs-4">
                            <img src="${c.user.avatar}" class="img-fluid rounded-circle" alt="avatar"/>
                        </div>
                        <div class="col-md-11 col-xs-8">
                            <span>${c.content}</span>
                             <p><em style="font-size: 13px">${moment(c.created_date).fromNow()}</em></p>
                        </div>
                    </div>
                ` + area.innerHTML
            } else if (data.status == 404)
                alert(data.err_msg)
        })
    }
}
