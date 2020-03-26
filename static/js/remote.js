const user = {
  name: null,
};

let live = false;

const toggleLive = (bool) => {
  const set = bool !== undefined ? !!bool : !live;
  if (set && !live) {
    // start
    getLocalStream();
    toggleUI(true);
    live = true;
  } else if (!set && live) {
    // stop
    toggleUI(false);
    disconnect();
    live = false;
  }
  // else you're dumb
}

const start = document.getElementById('start');
const end = document.getElementById('end');
const stream_ui = document.getElementById('stream');
const chat = document.getElementById('chat');

const toggleUI = (bool) => {
  if (bool) {
    start.classList.add(['d-none']);
    stream_ui.classList.remove(['d-none']);
    chat.classList.remove(['d-none']);
    end.classList.remove(['d-none']);
  } else {
    start.classList.remove(['d-none']);
    stream_ui.classList.add(['d-none']);
    chat.classList.add(['d-none']);
    end.classList.add(['d-none']);
  }
}

const startSteaming = (e) => {
  e.preventDefault();
  const name = document.getElementById('display_name');
  user.name = name.value;
  name.value = null;
  toggleLive(true);
  return false;
}

// Config variables: change them to point to your own servers
// WebRTC config: you don't have to change this for the example to work
// If you are testing on localhost, you can just use PC_CONFIG = {}
const PC_CONFIG = {
  iceServers: [
    {
      urls: 'stun:stun.l.google.com:19302',
    },
  ]
};

const disconnect = () => {
  socket.emit('leave', room);
  localStream.getTracks().forEach((track) => track.stop());
  localVideo.srcObject = localStream = null;
}

// Signaling methods
let socket;

let sendData = (data) => {
  socket.emit('data', {room, data});
};

function socketListeners(socket)
{
  socket.on('data', (data) => {
    console.log('Data received: ',data);
    handleSignalingData(data);
  });
  
  socket.on('ready', () => {
    console.log('Ready');
    // Connection with signaling server is ready, and so is local stream
    createPeerConnection();
    sendOffer();
  });
  
  socket.on('left', (sid) => {
    console.log(sid, 'left');
    remoteVideo.srcObject = null;
  });
}

// WebRTC methods
let pc;
let localStream;
let localVideo = document.getElementById('localVideo');
let remoteVideo = document.getElementById('remoteVideo');

let getLocalStream = () => {
  navigator.mediaDevices.getUserMedia({ audio: true, video: true })
    .then((stream) => {
      console.log('Stream found');
      localStream = stream;
      localVideo.srcObject = stream;

      // Connect after making sure that local stream is available
      socket = io();
      socketListeners(socket);
      socket.emit('join', room);
    })
    .catch(error => {
      console.error('Stream not found: ', error);
    });
}

let createPeerConnection = () => {
  try {
    pc = new RTCPeerConnection(PC_CONFIG);
    pc.onicecandidate = onIceCandidate;
    pc.onaddstream = onAddStream;
    pc.addStream(localStream);
    console.log('PeerConnection created');
  } catch (error) {
    console.error('PeerConnection failed: ', error);
  }
};

let sendOffer = () => {
  console.log('Send offer');
  pc.createOffer().then(
    setAndSendLocalDescription,
    (error) => { console.error('Send offer failed: ', error); }
  );
};

let sendAnswer = () => {
  console.log('Send answer');
  pc.createAnswer().then(
    setAndSendLocalDescription,
    (error) => { console.error('Send answer failed: ', error); }
  );
};

let setAndSendLocalDescription = (sessionDescription) => {
  pc.setLocalDescription(sessionDescription);
  console.log('Local description set');
  sendData(sessionDescription);
};

let onIceCandidate = (event) => {
  if (event.candidate) {
    console.log('ICE candidate');
    sendData({
      type: 'candidate',
      candidate: event.candidate
    });
  }
};

let onAddStream = (event) => {
  console.log('Add stream');
  remoteVideo.srcObject = event.stream;
};

let handleSignalingData = (data) => {
  switch (data.type) {
    case 'offer':
      createPeerConnection();
      pc.setRemoteDescription(new RTCSessionDescription(data));
      sendAnswer();
      break;
    case 'answer':
      pc.setRemoteDescription(new RTCSessionDescription(data));
      break;
    case 'candidate':
      pc.addIceCandidate(new RTCIceCandidate(data.candidate));
      break;
  }
};