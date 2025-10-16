import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './scss/app.css';
function App() {
    const [games, setGames] = useState([]);
    const [filteredGames, setFilteredGames] = useState([]);
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
  
    //Filtrar juegos en la búsqueda
    useEffect(() => {
      const q = query.toLowerCase();
      setFilteredGames(games.filter(g => g.nombre.toLowerCase().includes(q)));
    }, [query, games]);

    //Obtener precios cuando se selecciona un juego
    useEffect(()=>{
      if(!selectedGame) return;
      setLoadingPrices(true);

      fetch(`http://127.0.0.1:5000/api/prices?game_id=${selectedGame}`)
        .then(r=>r.json())
        .then(data=>{ setPrices(data); setLoadingPrices(false); })
        .catch(e=>{ console.error(e); setLoadingPrices(false); });
    },[selectedGame]);
  
    useEffect(() => {
      if (query.trim() === '') {
        setSelectedGame(null);
        setPrices([]); // opcional, limpia la tabla y el gráfico
      }
    }, [query]);
    
    const bestPrice = prices.length ? prices.reduce((a,b)=> a.precio < b.precio ? a : b) : null;

    return(
      <div>
        <header className="header">
          <div className="header-titulo">
            <h1>Comparador de Precios (Chile)</h1>
          </div>
          <div className="header-subtitulo">
            <span className="header-subtitulo-texto">Aquí encontraras el precio de los juegos entre las diversas tiendas (Steam, Epic, entre otros). </span>
          </div>
          <div className="test-txt">
            <span>(Versión de <strong>Pruebas</strong>)</span>
          </div>
        </header>
        
        <main className="main">
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
             <div className="buscar-juego-header">
              <div className="buscar-juego-titulo">
                <h2>Buscar juegos</h2>
              </div>

              <div className="buscar-juego-input">
                <input
                  list="juegos-sugerencias"
                  value={query}
                  onChange={e => {
                    const value = e.target.value;
                    setQuery(value);

                    const seleccionado = games.find(
                      g => g.nombre.toLowerCase() === value.toLowerCase()
                    );

                    if (seleccionado) {
                      setSelectedGame(seleccionado.id);
                      e.target.blur(); // cerrar el datalist
                    }
                  }}
                  placeholder="Escribe el nombre de un juego..."
                  className="w-full p-2 border rounded mb-3"
                  autoComplete="off"
                />

                <datalist id="juegos-sugerencias">
                  {filteredGames.slice(0, 15).map(g => (
                    <option key={g.id} value={g.nombre} />
                  ))}
                </datalist>
              </div>
            </div>

            {/* Info del juego seleccionado */}
            {!selectedGame && (
              <div className='juego-seleccionado'>
                <img loading="lazy" className="warning-icon" src="./public/warning.png"></img>
                <h3>Debes escribir en la barra de búsqueda el juego a cotizar.</h3>
              </div>
            )}
            {selectedGame && (
              <div className="juego-seleccionado">
                <img className='juego-seleccionado-cover' alt='juego-cover'></img>
                <h3 className="text-lg font-semibold mb-2">
                  {games.find(g => g.id === selectedGame)?.nombre}
                </h3>
                {/*<p className="text-sm text-gray-600 mb-3">
                  Slug: {games.find(g => g.id === selectedGame)?.slug}
                </p>*/}

                {loadingPrices ? (
                  <p>Cargando precios...</p>
                ) : prices.length > 0 ? (
                  <ul>
                    {prices.map((p, i) => (
                      <li key={i} className="border-t py-1">
                        {p.tienda}: {p.precio} {p.moneda}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500">No hay precios disponibles.</p>
                )}
              </div>
            )}
          </section>
    
          
          {selectedGame &&(
            <section className='comparacion-precios'>
            <div className='comparacion-precios-header'>
              <h2>Comparación</h2>
            </div>

            

            {selectedGame && (
              <div className="comparacion-precios-detalle">
                <div className="mejor-precio">
                  <strong>Mejor precio:</strong>{' '}
                  {bestPrice
                    ? `$${bestPrice.precio} en ${bestPrice.tienda}` /*${bestPrice.moneda} */
                    : loadingPrices
                    ? 'Cargando...'
                    : 'No hay precios disponibles'}
                </div>

                {loadingPrices ? (
                  <div>Cargando precios...</div>
                ) : prices.length > 0 ? (
                  <>
                    {/* Tabla de precios */}
                    <div className="comparacion-precios-grafico">

                        <div className="tabla-precios">
                          <table className="w-full table-auto border-collapse mb-6">
                            <thead>
                              <tr className="text-left border-b">
                                <th className="p-2">Tienda</th>
                                <th className="p-2">Precio</th>
                                <th className="p-2">Moneda</th>
                                <th className="p-2">Fecha</th>
                              </tr>
                            </thead>
                            <tbody>
                              {prices.map((p, i) => (
                                <tr
                                  key={i}
                                  className={`${
                                    bestPrice && p.precio === bestPrice.precio ? 'bg-green-50' : ''
                                  }`}
                                >
                                  <td className="p-2">{p.tienda}</td>
                                  <td className="p-2">{p.precio}</td>
                                  <td className="p-2">{p.moneda}</td>
                                  <td className="p-2">
                                    {new Date(p.fecha).toLocaleDateString()}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>

                      <div className='rechart'>
                        <ResponsiveContainer width="100%" minHeight="10rem">
                          <LineChart data={prices}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis
                              dataKey="fecha"
                              tickFormatter={(f) =>
                                new Date(f).toLocaleDateString('es-CL', {
                                  day: '2-digit',
                                  month: 'short',
                                })
                              }
                            />
                            <YAxis />
                            <Tooltip
                              formatter={(v, n, props) => [`$${v}`, props.payload.tienda]}
                              labelFormatter={(f) =>
                                new Date(f).toLocaleString('es-CL', {
                                  day: '2-digit',
                                  month: 'short',
                                  year: '2-digit',
                                })
                              }
                            />
                            <Legend />
                            <Line
                              type="monotone"
                              dataKey="precio"
                              name="Precio"
                              stroke="#0077ff"
                              activeDot={{ r: 6 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>

                    </div>
                    

                    
                    
                  </>
                ) : (
                  <div>No hay precios registrados para este juego.</div>
                )}
              </div>
            )}
          </section>


          )}
          
          
          
          <section className= "sobre-nosotros">
              <div className="disclaimer">
                <span className="disclaimer-text">**Datos recolectados de APIs de terceros. No afiliado a Steam/Epic ni los distribuidores mostrados. Los precios pueden variar según el cambio de moneda.</span>
              </div>
              <div className= "rrss">
                <h4 className= "Titulo-2"> Nuestras Redes</h4>
                <ul>
                  <li>
                    <img loading="lazy" className="rrss_img" alt="yt_icon" src="./public/youtube_icon.png"></img>
                  </li>
                </ul>
              </div>
              <div className="contacto">
                <h4 className="Titulo-2">Contacto</h4>
                <p>Si tienes dudas, o presentas problemas con la página. No dudes en contactarnos por los siguientes medios:</p>
                <ul>
                  <li>Email:</li>
                </ul>
              </div>
            
          </section>
        </main>
        <footer className="footer">
          <span className="copyright">Todos los derechos reservados, 2025</span>
          
        </footer>
      </div>
    );
  
}

export default App;
