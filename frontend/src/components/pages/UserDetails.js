import { React, Component } from 'react';
import {ForceGraph2D } from 'react-force-graph';
import withRouter from '../../utils/reactRouterV6BackCompUtils';

class UserDetails extends Component {
    constructor(props) {
        super(props);
        console.log("UserDetails initialized");
        this.state = {
            nodes: [],
            links: []
        }
    }
    

    componentDidMount() {
        console.log(this.props);
        const user_uuid = this.props.router.params.id
        this.callApi(user_uuid)
            .then(res => {
                let data = res.data;
                let nodeList = [];
                let edgeList = [];
                let rootNode = {};
                for (const [key, value] of Object.entries(data)) {
                    console.log(key)
                    if (key !== "TWEETED") rootNode[key] = value;
                }
                console.log(rootNode);
                nodeList.push(rootNode);
                data["TWEETED"].forEach(el => {
                    nodeList.push(el);
                    edgeList.push({"source": rootNode.uuid, "target": el.uuid, "edge_type": "TWEETED"})
                });
                this.setState({ nodes: nodeList, links: edgeList });
                console.log(this.state);
            })
            .catch(err => console.log(err));
        console.log(this.state);
    }

    callApi = async (uuid) => {
        const response = await fetch(`http://localhost:5000/get-graph-user/${uuid}`)
        const body = await response.json();
        if (!response.ok) throw Error(body.message);
        return body;
    }

    getTooltip = (node) => {
        var tooltip = '';
        if (node.labels === null || node.labels === undefined) {
            return ''
        }
        else if (node.labels.includes('Troll')) {
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



    render() {
        return (
            <div>
                <h1>User Details</h1>
                <div className='container-graph'>
                    <ForceGraph2D 
                        graphData={this.state} 
                        nodeId='uuid'
                        nodeLabel={node => this.getTooltip(node)}
                        linkLabel={link => link.edge_type}
                    />
                </div>
            </div>
        );
    }
    
};
  
export default withRouter(UserDetails);