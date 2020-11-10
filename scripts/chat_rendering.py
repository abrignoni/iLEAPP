# coding: utf-8

"""
This helper renders chat conversations passed as a json dump of a dictionary:
    --conversation contact id/name
        --num message (start from 0 each time is fine)
            --data-name = correspondant (phone or ID)
            --data-time = time of message (formatted as str)
            --from_me = (boolean - 0 = received / 1 = sent)
            --message = message content

example:
    {
        "Vincent":{
            "0":{
                "data-name": "Vincent",
                "data-time": "2020-11-10 08:00:00",
                "from_me" : 0,
                "Message": "What is your favorite tool?"
            },
            "1":{
                "data-name": "Vincent",
                "data-time": "2020-11-10 08:01:00",
                "from_me" : 1,
                "Message": "iLEAPP !"
            },
        },
        "Mike,Vincent":{
            "0":{
                "data-name": "Mike",
                "data-time": "2020-11-10 08:08:00",
                "from_me" : 0,
                "Message": "Who like apples ?"
            },
            "1":{
                "data-name": "Vincent",
                "data-time": "2020-11-10 08:09:00",
                "from_me" : 1,
                "Message": "I do!"
            }
    }

"""
import json

HTML= """
<div class="container clearfix">
    <div class="people-list" id="people-list">
      <ul class="list" id="list">

      </ul>
    </div>
    <div class="chat">
      <div class="chat-header clearfix">


        <div class="chat-about">
          <div class="chat-with" id="chat-with">Click on the left to view messages</div>
          <div class="chat-num-messages" id="chat-num-messages"></div>
        </div>
        </div> <!-- end chat-header -->
        <div id="chat-history" class="chat-history">
        </div>
    </div>
</div>
<br />
<br />
"""
js = """
<script>
function createDivMessages (m){

    var messType = '<div class="message my-message">';
    var liTag = '<li>';
    var messDataTag = '<div class="message-data">';
    var name = m["data-name"];

    if (m["from_me"] == 1) {
        messType = '<div class="message other-message float-right">';
        liTag = '<li class="clearfix">'
        messDataTag = '<div class="message-data align-right">';
        name = "Me";
    }

    var res = liTag;
    res += messDataTag;
    res += '<span class="message-data-time" >';
    res += m["data-time"];
    res += '</span> &nbsp; &nbsp;';
    res += '<span class="message-data-name" >';
    res += name;
    res += '</span>';
    res += '</div>';
    res += messType;
    res += m["message"];
    res += '</div>';
    res += '</li>';

    return res;
}

function showHistory (messages, name){

    html = "<ul>";
    for (let m in messages){
      html += createDivMessages(messages[m], name);
    }
    html += "</ul>";
    $("#chat-history").html(html);
    return false;
}

function createPeopleList(list){

    var res = '';
    for (let p in list){
        res += '<li class="clearfix" id="';
        res += list[p];
        res += '">';
        res +=  '<div class="about">';
        res +=    '<div class="name">';
        res += list[p];
        res += '</div>';
        res +=  '</div>';
        res += '</li>';
    }
    $("#list").html(res);
}

function updateHeader(name, num){
    $("#chat-with").html(name);
    $("#chat-num-messages").html("Total: "+num)
    return false;
}

$(document).ready(function() {
    var messages = JSON.parse(json);

    createPeopleList(Object.keys(messages));

    $('.people-list li').click(function(){
        $(this).addClass('active').siblings().removeClass('active');
        var id = $(this).attr('id');
        showHistory(messages[id]);
        updateHeader(id,Object.keys(messages[id]).length);
        return false;
    });
});
</script>
"""

def render_chat(chat_json):
    json_js = """
    <script>
     var json = {0!r};
    </script>
    """.format(chat_json)
    return {'HTML':HTML,'js':'\n'.join([json_js,js])}

