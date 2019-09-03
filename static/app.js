/*
 * Copyright 2019 Genentech Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

$(document).ready(function () {
  $('[rel="popover"]').popover(
    {container: 'body'}
  );

  if(window.WebSocket) {
    start_websocket();
    // control_websocket()
  }
  else {
    bootbox.alert({message: "This Browser Does Not Support Websockets... Try recent versions of chrome, safari, or firefox!",
                  backdrop: false
                });
  }

  $("#console").scrollTop = 1500;

  function start_websocket() {
    if (window.location.port == null){
      ws_url = "ws://" + window.location.hostname + "/websocket";
    } else {
      ws_url = "ws://" + window.location.hostname + ":"+window.location.port+"/websocket";
    }
    // bootbox.alert(ws_url)
    var ws = new WebSocket(ws_url);
    ws.onopen = function(){
      ws.send(JSON.stringify({command:"initialize", data:{}}));
    };
    ws.onmessage = function(msg){
      data_object = JSON.parse(msg.data)
      switch(data_object.type) {
        case "gallery":
          $('img').tooltip('hide');
          $("#replaceme").html(data_object.data);
          $('[data-toggle="tooltip"]').tooltip(
            {container: 'body',
            placement: 'bottom'}
          );
          break;
        case "alert":
          bootbox.alert(data_object.data)
      }
    };

    $(document).off('click',"[data-toggle='lightbox']");
    $(document).on('click', '[data-toggle="lightbox"]', function(event) {
                    event.preventDefault();
                    $(this).ekkoLightbox({
                      showArrows: false,
                    });
    });

    $(document).off('click',"#update-warp-directory");
    $(document).on('click', '#update-warp-directory', function(event) {
      bootbox.prompt({
        title: "Enter the directory name for your new Warp directory.",
        closeButton: false,
        callback: function(result) {
          message = {"command": "change_directory", "data": result}
          if (message != null) {
            ws.send(JSON.stringify(message));
          }
        }
      });
    });
  }
});
