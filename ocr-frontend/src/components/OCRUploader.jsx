// npm start
import React, { useState } from 'react';
import axios from 'axios';
import '../styles/style.css';

const OCRUploader = () => {
  const [file, setFile] = useState(null);
  const [model, setModel] = useState('trocr');
  const [text, setText] = useState('');
  const [editableText, setEditableText] = useState('');
  const [timer, setTimer] = useState(0);
  const [loading, setLoading] = useState(false);

  const handleExtract = async () => {
    if (!file) return alert("Please upload an image.");
    setLoading(true);
    setText('');
    setEditableText('');
    const start = performance.now();

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`http://127.0.0.1:8000/api/translate?model=${model}`, formData);
      setText(res.data.text);
      setEditableText(res.data.text);
      const end = performance.now();
      setTimer(((end - start) / 1000).toFixed(2));
    } catch (error) {
      setText("Error: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Section 1: Navbar */}
      <nav className="navbar">OCR Web App</nav>

      {/* Section 2: Upload + Extract */}
      <div className="main-section">
        <div className="left-panel">
          <input type="file" accept="image/*" onChange={e => setFile(e.target.files[0])} />
          <select value={model} onChange={e => setModel(e.target.value)}>
            <option value="trocr">TrOCR</option>
            <option value="easyocr">EasyOCR</option>
            <option value="tesseract">Tesseract</option>
            <option value="donut">Donut</option>
            <option value="ocrvit">OCR-ViT</option>
          </select>
          <button onClick={handleExtract} disabled={loading}>
            {loading ? "Extracting..." : "Extract"}
          </button>
          {timer > 0 && <div className="timer">⏱ Time Taken: {timer}s</div>}
        </div>

        <div className="right-panel">
          <label>Extracted Text (Read-only)</label>
          <textarea readOnly value={text}></textarea>
        </div>
      </div>

      {/* Section 3: Editable Text */}
      <div className="editable-section">
        <label>Edit Extracted Text</label>
        <textarea value={editableText} onChange={(e) => setEditableText(e.target.value)} />
      </div>

      {/* Section 4: Footer */}
      <footer className="footer">© NIT INTERNSHIP</footer>
    </div>
  );
};
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
// or process.env.REACT_APP_BACKEND_URL

const res = await axios.post(
  `${BACKEND_URL}/api/translate?model=${model}`,
  formData
);


export default OCRUploader;
