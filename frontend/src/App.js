import logo from './logo.svg';
import './App.css';
import 'rc-menu/assets/index.css';
import NavMenu from './components/NavMenu';
import { Outlet } from 'react-router-dom';

function App() {
  return (
    
          <div className="App">
            <div style={{ margin: 20 }}>
              <NavMenu mode='horizontal'>
              </NavMenu>
            </div>
            <Outlet />
          </div>
  );
}

export default App;
