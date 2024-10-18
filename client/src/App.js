import React, { useState, useEffect } from 'react';
import './App.css';
import { AP } from "./components/AP.jsx";

function App() {
  const [data, setData] = useState([]);
  const [sortedData, setSortedData] = useState([]);
  const [sortCriteria, setSortCriteria] = useState(null); // Store current sorting criteria
  const [imageSrc, setImageSrc] = useState(null); // New state for the image
  const [currentWifi, setCurrentWifi] = useState(null); // Store the ESSID of the current Wi-Fi

  useEffect(() => {
    const fetchData = () => {
      fetch("http://127.0.0.1:5000/PickYourWifi")
        .then(res => res.json())
        .then(receivedData => {
          setData(receivedData);
          // Determine the currently connected Wi-Fi
          const inUseAP = receivedData.find(ap => ap["IN-USE"] === "*");
          if (inUseAP) {
            setCurrentWifi(inUseAP.SSID); // Store the current Wi-Fi ESSID
          }

          // Maintain the current sorted state based on previous criteria
          if (sortCriteria === 'rate') {
            sortByRate(receivedData);
          } else if (sortCriteria === 'signal') {
            sortBySignal(receivedData);
          } else {
            setSortedData(receivedData); // Default to unsorted data
          }
          console.log("Received data:", receivedData);
        })
        .catch(error => console.error("Error fetching data:", error));
    };

    fetchData();

    const intervalId = setInterval(fetchData, 2000); // Fetch data every 2 seconds

    return () => clearInterval(intervalId);
  }, [sortCriteria]); // Add sortCriteria to dependencies

  // New useEffect to fetch the Wi-Fi signal graph image
  useEffect(() => {
    const fetchImage = () => {
      if (currentWifi) {
        // Update the image URL by appending a timestamp to prevent caching
        setImageSrc(`http://127.0.0.1:5000/wifi-signal-graph?timestamp=${new Date().getTime()}`);
      }
    };

    fetchImage();
    const imageIntervalId = setInterval(fetchImage, 2000); // Fetch the image every 2 seconds only if current Wi-Fi is present

    return () => clearInterval(imageIntervalId);
  }, [currentWifi]); // Fetch image based on the current Wi-Fi

  const sortByRate = (dataToSort) => {
    const sorted = [...dataToSort].sort((a, b) => {
      const rateA = parseFloat(a.RATE) || 0;
      const rateB = parseFloat(b.RATE) || 0;
      return rateB - rateA; // Sort descending
    });
    setSortedData(sorted);
    setSortCriteria('rate'); // Update sorting criteria
  };

  const sortBySignal = (dataToSort) => {
    const sorted = [...dataToSort].sort((a, b) => {
      const signalA = parseFloat(a.SIGNAL) || 0;
      const signalB = parseFloat(b.SIGNAL) || 0;
      return signalB - signalA; // Sort descending
    });
    setSortedData(sorted);
    setSortCriteria('signal'); // Update sorting criteria
  };

  return (
    <div className="App">
      <div className="title">APtracker</div>
      <div className="sort-buttons">
        <button
          onClick={() => sortByRate(data)}
          className={sortCriteria === 'rate' ? 'active' : ''}
        >
          Sort by Rate
        </button>
        <button
          onClick={() => sortBySignal(data)}
          className={sortCriteria === 'signal' ? 'active' : ''}
        >
          Sort by Signal
        </button>
      </div>
      {currentWifi && (
        <div className="signal-graph">
          {imageSrc && <img className="the-image" src={imageSrc} alt="Wi-Fi Signal Graph" />}
        </div>
      )}
      {sortedData.map((element, index) => (
        <AP key={index} data={element} />
      ))}



    </div>
  );
}

export default App;
