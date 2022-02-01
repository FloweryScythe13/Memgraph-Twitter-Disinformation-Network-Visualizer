import React, { useState, use } from "react";
import { Link } from 'react-router-dom';

const ContextMenu = (props) => {
  // Leaving this reference link on array destructuring here for Memgraph reviewers:
  //https://reactjs.org/docs/hooks-state.html#tip-what-do-square-brackets-mean
  //const [selectedNodeId, setSelectedNodeId] = useState(props.selectedNodeId);
  const selectedNodeId = props.selectedNodeId;
  // const onNodeClick = (node) => {
  //   setSelectedNodeId(node.id);
  // };
  const onCloseClick = (e) => {
    props.clickHandler(e);
  }
  const [topVal, leftVal] = [props.menuStyle.top, props.menuStyle.left];
 
  return (
          <div style={{ zIndex: 1, position: 'fixed', backgroundColor: 'white', top: topVal, left: leftVal}}>
            <div>NODE MENU FOR {selectedNodeId}</div>
            <br />
            <div><Link to={`../UserDetails/${selectedNodeId}`} >Go to User Details</Link></div>
            <button onClick={onCloseClick}>Close</button>
          </div>
        )
};

export default ContextMenu;