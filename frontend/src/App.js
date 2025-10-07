
//import './App.css';
import React, { useEffect, useState } from 'react';
function App() {
  const [games, setGames] = useState([]);
    const [selectedGame, setSelectedGame] = useState(null);
    const [prices, setPrices] = useState([]);
    const [loadingGames, setLoadingGames] = useState(false);
    const [loadingPrices, setLoadingPrices] = useState(false);
    const [query, setQuery] = useState('');
  
    useEffect(()=>{
      setLoadingGames(true);
      fetch('http://127.0.0.1:5000/api/games')
        .then(r=>r.json())
        .then(data=>{ setGames(data); setLoadingGames(false); })
        .catch(e=>{ console.error(e); setLoadingGames(false); });
    },[]);
  
    useEffect(()=>{
      if(!selectedGame) return;
      setLoadingPrices(true);
      fetch(`/api/prices?game_id=${selectedGame}`)
        .then(r=>r.json())
        .then(data=>{ setPrices(data); setLoadingPrices(false); })
        .catch(e=>{ console.error(e); setLoadingPrices(false); });
    },[selectedGame]);
  
    const filteredGames = games.filter(g => g.nombre.toLowerCase().includes(query.toLowerCase()));
    const bestPrice = prices.length ? prices.reduce((a,b)=> a.precio < b.precio ? a : b) : null;

    return(
      <div>
        <header className="header color-principal">
          <h1>Comparador de Precios (Chile)</h1>
          <p className="">Comparador de precios - datos desde Steam, Epic y otras tiendas.</p>
        </header>
        <main className="">
          <section className='juegos-recomendados'>
            <div className='juegos-recomendados-header'>
              <h2>Recomendados</h2>
            </div>
            <ul>
              <li className='item'>
                <div className='item-card'>
                  <img className='item-img'></img>
                  <h3 className='item-title'>Cyberpunk 2077</h3>
                  <h3 className='item-price'>$11111</h3>
                  <button>Ver mas</button>

                </div>
              </li>
            </ul>
          </section>
          
          <section className="buscar-juego">
            <div className= "buscar-juego-header">
              <h2 className="buscar-juego-titulo">Juegos</h2>
              <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Buscar juego..." className="w-full p-2 border rounded mb-3" />
            </div>
            
            {
              loadingGames 
              ? <div>Cargando juegos...</div>
              : <ul>
                {filteredGames.map( g => (
                <li key={g.id}>
                  <div >{g.nombre}</div>
                  <div >{g.slug}</div>
                </li>
              ))}
              </ul>
            }
          </section>
          <section className='comparacion-precios'>
            <div className='comparacion-precios-header'>
              <h2>Comparación</h2>
            </div>
            {!selectedGame && <div>Selecciona un juego para ver los precios.</div>}
            {selectedGame && (
              <div>
                <div className="">
                  <strong>Mejor precio:</strong> 
                  {
                    bestPrice ? 
                    `${bestPrice.precio} ${bestPrice.moneda} en ${bestPrice.tienda}` 
                    : (loadingPrices ? 'Cargando...' : 'No hay precios')
                  }
                </div>
                {
                  loadingPrices ? (
                    <div>Cargando precios...</div>
                  ) : (
                    <table className="w-full table-auto border-collapse">
                      <thead>
                        <tr className="text-left border-b">
                          <th className="p-2">Tienda</th>
                          <th className="p-2">Precio</th>
                          <th className="p-2">Moneda</th>
                          <th className="p-2">Fecha</th>
                        </tr>
                      </thead>
                      <tbody>
                        {prices.map((p, i)=>(
                          <tr key={i} className={`${bestPrice && p.precio===bestPrice.precio ? 'bg-green-50':''}`}>
                            <td className="p-2">{p.tienda}</td>
                            <td className="p-2">{p.precio}</td>
                            <td className="p-2">{p.moneda}</td>
                            <td className="p-2">{new Date(p.fecha).toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )
                }
              </div>
            )
            }
          </section>
        </main>
        <footer className="footer">
          <span className="copyright">Todos los derechos reservados, 2025</span>
          <span className="disclaimer">**Datos recolectados de APIs públicas. No afiliado a Steam/Epic ni distribuidores locales.</span>
        </footer>
      </div>
    );
  /*return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );*/
}

export default App;
