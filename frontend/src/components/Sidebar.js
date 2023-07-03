import { React, Component } from 'react';

class Sidebar extends Component {
    constructor(props) {
        super(props);
        this.state = {
            statistics: []
        }
    }
    
    componentDidMount() {
        this.callApi()
            .then(res => this.setState({ statistics: res.data }))
            .catch(err => console.log(err));
    }

    callApi = async () => {
        const response = await fetch('http://localhost:5000/get-graph/properties')
        const body = await response.json();
        if (!response.ok) throw Error(body.message);
        return body;
    }

    toCamelCaseListKey = (str) => {
        str.replace(/\s(.)/g, (a) => a.toUpperCase())
            .replace(/\s/g, '')
            .replace(/^(.)/, (b) => b.toLowerCase());
    }
    

    render() {
        const ref = this;
        const networkStatisticsList = this.state.statistics.map((item) => {
            let itemName = ref.toCamelCaseListKey(item.name);
            return (
                <li key={itemName}>
                    <ul className='stat-list'>
                        <li key={itemName + "-name"} className='stat-name'>{item.name}</li>
                        <li key={itemName + "-value"} className='stat stat-value'>{item.value}</li>
                    </ul>
                </li>
            )
        }
            
        );

        return (
            <div style={{position: "fixed", right: "0px", display: "inline-block", zIndex: "10918293!important", width: "auto", marginRight: "0px", clear: "both"}}>
                <div id="networkStatistics" className='network-stats-view'>
                    <ul className="network-stats-list">
                        {networkStatisticsList}
                    </ul>
                </div>
            </div>
        );
    }
    
};
  
export default Sidebar;