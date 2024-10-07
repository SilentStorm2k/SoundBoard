// components/Soundboard.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Soundboard({ setIsAuthenticated }) {
  const [sounds, setSounds] = useState([]);
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchSounds();
  }, []);

  const fetchSounds = async () => {
    try {
      const response = await fetch('http://localhost:8000/sounds/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      if (response.ok) {
        const data = await response.json();
        setSounds(data);
      } else {
        throw new Error('Failed to fetch sounds');
      }
    } catch (error) {
      console.error('Error fetching sounds:', error);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload-sound/', {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: formData,
      });
      if (response.ok) {
        alert('Sound uploaded successfully');
        fetchSounds();
      } else {
        throw new Error('Failed to upload sound');
      }
    } catch (error) {
      console.error('Error uploading sound:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    navigate('/login');
  };

  const playSound = (url) => {
    const audio = new Audio(url);
    audio.play();
  };

  return (
    <div>
      <h2>Soundboard</h2>
      <button onClick={handleLogout}>Logout</button>
      <div>
        <h3>Upload Sound</h3>
        <form onSubmit={handleUpload}>
          <input type="file" accept="audio/*" onChange={handleFileChange} />
          <button type="submit">Upload</button>
        </form>
      </div>
      <div>
        <h3>Your Sounds</h3>
        {sounds.map((sound) => (
          <button key={sound.id} onClick={() => playSound(sound.sound_url)}>
            {sound.sound_name}
          </button>
        ))}
      </div>
    </div>
  );
}

export default Soundboard;