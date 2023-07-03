import { React, Component, useCallback, createRef } from 'react';
import { createPortal } from 'react-dom';
import Container from "react-bootstrap/Container";
import { ForceGraph3D } from 'react-force-graph';
import { Sprite, SpriteMaterial, TextureLoader, LinearFilter, Group } from 'three';
import SpriteText from 'three-spritetext';
import { useForm } from 'react-hook-form';
import trollImage from '../../troll-matrioshka-doll.jpg'
import userImage from '../../user-stock-icon.jpg';
import Sidebar from '../Sidebar';
import ContextMenu from '../ContextMenu';

class NorthAfrica extends Component {
    constructor(props) {
        super(props);
        console.log("NorthAfrica initialized");
        this.closeContextMenu = this.closeContextMenu.bind(this);
        this.callApiNoRetweets = this.callApiNoRetweets.bind(this);
        this.myRef = createRef();
        this.state = {
            nodes: [],
            links: [],
            nodeRightClickCoordinates: {},
            contextMenuShow: false,
            contextMenu: {},
            selectedNodeId: null
        }
    }
    
    closeContextMenu(event) {
        console.log("closeContextMenu called");
        if(this.state.selectedNodeId) {
            console.log("selectedNodeId is true");
            this.setState({selectedNodeId: null})
        }
    }

    componentDidMount() {
        this.loadFullGraph();
        console.log(this.state);
        //document.addEventListener("mousedown", this.closeContextMenu);
    }

    loadFullGraph = () => {
        this.callApi()
            .then(res => this.setState({ nodes: res.nodes, links: res.links }))
            .catch(err => console.log(err));
    }
    // componentWillUnmount() {
    //     document.removeEventListener('mousedown', this.closeContextMenu)
    // }

    filterRetweets = (event) => {
        console.log("button clicked")
        this.callApiNoRetweets()
        .then(res => this.setState({ nodes: res.nodes, links: res.links }))
        .catch(err => console.log(err));
    }

    filterSources = (event) => {
        this.callApiNoSources()
            .then(res => this.setState({ nodes: res.nodes, links: res.links }))
            .catch(err => console.log(err));
    }

    callApi = async () => {
        const response = await fetch('http://localhost:5000/get-graph')
        const body = await response.json();
        if (!response.ok) throw Error(body.message);
        return body;
    }

    callApiNoRetweets = async () => {
        const response = await fetch('http://localhost:5000/get-graph-no-retweets')
        const body = await response.json();
        if (!response.ok) throw Error(body.message);
        return body;
    }

    callApiNoSources = async () => {
        const response = await fetch('http://localhost:5000/get-graph-no-sources')
        const body = await response.json();
        if (!response.ok) throw Error(body.message);
        return body;
    }

    callGetUser = async (id) => {
        const response = await fetch(`http://localhost:5000/get-twitter-user/${id}`)
        const body = await response.json();
        if (!response.ok) throw Error(body.message);
        return body;
    }

    onNodeClick = (node, event) => {
        console.log("click");
        console.log(node);
        console.log(event);
        this.setState({selectedNodeId: node.uuid, contextMenu: {
            ...this.state.contextMenu, 
            top: event.clientY - event.target.offsetTop,
            left: event.clientX - event.target.offsetLeft
        }});
        console.log(this.state.contextMenu);
    }

    // onNodeRightClick = (node, event) => {
    //     if (node) {

    //         this.setState({
    //             selectedNodeId: node.uuid,
    //             nodeRightClickCoordinates: (this.myRef.current
    //                 ? this.myRef.current.graph2ScreenCoords(
    //                     node.x,
    //                     node.y
    //                 )
    //                 : null)
    //         })
    //     }
    // }

    getTooltip = (node) => {
        var tooltip = '';
        if (node.labels.includes('Troll')) {
            tooltip = `<div style="color:#333333;padding:12px;background: white;border-radius: 2px;">
            <div style="font-weight:bold; margin-bottom:16px;"><strong>Troll: ${node.id}</strong></div>
            <div class="keyval">
                <div class="key">Screen Name:</div>
                <div class="val">${node.user_screen_name}</div>
            </div>
            <div class="keyval">
                <div class="key">Followers:</div>
                <div class="val">${node.follower_count}</div>
            </div>
            <div class="keyval">
                <div class="key">Following:</div>
                <div class="val">${node.following_count}</div>
            </div>
            <div class="keyval">
                <div class="key">Language:</div>
                <div class="val">${node.language}</div>
            </div>
            <div class="keyval">
                <div class="key">User-Reported Location:</div>
                <div class="val">${node.user_reported_location}</div>
            </div>
        </div>`
        }
        else if (node.labels.includes("Tweet")) {
            tooltip = `<div style="color:#333333;padding:12px;background: white;border-radius: 2px;">
            <div style="font-weight:bold; margin-bottom:16px;"><strong>Tweet: ${node.id}</strong></div>
            <div class="keyval">
                <div class="key">Tweet Text:</div>
                <div class="val">${node.text}</div>
            </div>
            <div class="keyval">
                <div class="key">Replies:</div>
                <div class="val">${node.replies_count}</div>
            </div>
            <div class="keyval">
                <div class="key">Retweets:</div>
                <div class="val">${node.retweets_count}</div>
            </div>
            <div class="keyval">
                <div class="key">Quotes:</div>
                <div class="val">${node.quote_count}</div>
            </div>
            <div class="keyval">
                <div class="key">Likes:</div>
                <div class="val">${node.like_count}</div>
            </div>
        </div>`
        }
        else if (node.labels.includes("Hashtag") || node.labels.includes("Source")) {
            tooltip = `<div><b>${node.labels[0]}</b>: <span>${node.name}</span></div>`;
        }
        return tooltip;
    }

    // getContextMenu = useCallback(node => {
    //     var menu = '';
    //     // if (node.labels.includes('Troll')) {
    //         menu = (
    //             <div style="color:#333333;padding:12px;background: white;border-radius: 2px;">
    //                 <div style="font-weight:bold; margin-bottom:16px;"><strong>Troll: ${node.id}</strong></div>
    //                 <div class="keyval">
    //                     <div class="key">Screen Name:</div>
    //                     <div class="val">${node.user_screen_name}</div>
    //                 </div>
    //                 <div><Link to="/UserDetails/${node.uuid}">Get User Details</Link></div>
    //             </div>
    //         )
    //     // }
    //     return menu;
    // })

    render() {
        let selectedNodeId = this.state.selectedNodeId;
        let menuStyle = this.state.contextMenu;
        let contextMenuCoordinates = this.state.nodeRightClickCoordinates;
        return (
            <Container fluid>
                <h1>IRA Network: North Africa</h1>
                <div className='container-graph big-graph-window'>
                    {selectedNodeId && createPortal(
                        <ContextMenu selectedNodeId={selectedNodeId} menuStyle={menuStyle} nodeRightClickCoordinates={contextMenuCoordinates} clickHandler={this.closeContextMenu}/>,
                        document.body
                    )}
                    <div className='filter-menu' id="filter-menu">
                    <button className='btn btn-default btn-margin-right' onClick={this.filterRetweets}>Filter on Tweets (no retweets)</button>
                    <button className='btn btn-default btn-margin-right' onClick={this.filterSources}>Filter on Tweet Sources</button>
                    <button className='btn btn-default btn-margin-right' onClick={this.loadFullGraph}>Restore Full Graph</button>
                    </div>
                    <ForceGraph3D 
                        graphData={this.state} 
                        ref={this.myRef}
                        nodeAutoColorBy="group"
                        nodeThreeObject={node => {
                            let sprite = null;
                            if (node.labels.includes("Troll")) {
                                // let spriteText = new SpriteText(node.id);
                                // spriteText.color = node.color;

                                let map = new TextureLoader().load(trollImage);
                                map.minFilter = LinearFilter;
                                const material = new SpriteMaterial({ map: map });
                                const spriteImage = new Sprite(material);
                                spriteImage.scale.set(20,20,1);

                                // // combine the sprites as a group
                                // var group = new Group();
                                // group.add( spriteText );
                                // group.add( spriteImage );
                                // sprite = group;
                                sprite = spriteImage;
                            }
                            else if (node.labels.includes("User")) {
                                let map = new TextureLoader().load(userImage);
                                map.minFilter = LinearFilter;
                                const material = new SpriteMaterial({ map: map });
                                const spriteImage = new Sprite(material);
                                spriteImage.scale.set(11,11,1);
                                sprite = spriteImage;
                            }  
                            else if (node.labels.includes("Hashtag"))
                                sprite = new SpriteText(`#${node.name}`)
                            else sprite = new SpriteText(node.id)
                            sprite.color = node.color;
                            sprite.textHeight = 8;
                            return sprite;
                        }}
                        nodeLabel={node => this.getTooltip(node)}
                        nodeAutoColorBy={node => node.labels}
                        linkLabel={link => link.edge_type}
                        onNodeClick={this.onNodeClick}
                    />
                </div>
                
                <Sidebar />
            </Container>
        );
    }
    
};
  
export default NorthAfrica;