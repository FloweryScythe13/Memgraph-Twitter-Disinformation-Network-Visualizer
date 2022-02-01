import React from 'react';
import PropTypes from 'prop-types';
import Menu, { SubMenu, Item as MenuItem, Divider } from 'rc-menu';
import 'rc-menu/assets/index.css';
import animate from 'css-animation';
import { Link } from 'react-router-dom';

function handleClick(info) {
  console.log(`clicked ${info.key}`);
  console.log(info);
}

const animation = {
  enter(node, done) {
    let height;
    return animate(node, 'rc-menu-collapse', {
      start() {
        height = node.offsetHeight;
        node.style.height = 0;
      },
      active() {
        node.style.height = `${height}px`;
      },
      end() {
        node.style.height = '';
        done();
      },
    });
  },

  appear() {
    return this.enter.apply(this, arguments);
  },

  leave(node, done) {
    return animate(node, 'rc-menu-collapse', {
      start() {
        node.style.height = `${node.offsetHeight}px`;
      },
      active() {
        node.style.height = 0;
      },
      end() {
        node.style.height = '';
        done();
      },
    });
  },
};


function onOpenChange(value) {
  console.log('onOpenChange', value);
}


const customizeIndicator = <span>Add More Items</span>;

class NavMenu extends React.Component {
  state={
    overflowedIndicator: undefined,
  }

  toggleOverflowedIndicator = () => {
    this.setState({
      overflowedIndicator:
        this.state.overflowedIndicator === undefined ?
          customizeIndicator :
          undefined,
    });
  }
  render() {
    const { overflowedIndicator } = this.state;
    return (
      <div>
        {this.props.updateChildrenAndOverflowedIndicator && <div>
          <button onClick={this.toggleOverflowedIndicator}>toggle overflowedIndicator</button>
        </div>}
        <Menu
          onClick={handleClick}
          onOpenChange={onOpenChange}
          selectedKeys={['3']}
          mode={this.props.mode}
          openAnimation={this.props.openAnimation}
          defaultOpenKeys={this.props.defaultOpenKeys}
          overflowedIndicator={overflowedIndicator}
        >
            <SubMenu title={<span className="submenu-title-wrapper">Past IRA Campaigns</span>} key="1">
                <MenuItem key="1-1">
                    <Link to="/NorthAfrica">Northern Africa</Link>
                </MenuItem>
            </SubMenu>
        </Menu>
      </div>
    );
  }
}

NavMenu.propTypes = {
  mode: PropTypes.string,
  openAnimation: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  triggerSubMenuAction: PropTypes.string,
  defaultOpenKeys: PropTypes.arrayOf(PropTypes.string),
  updateChildrenAndOverflowedIndicator: PropTypes.bool,
};

export default NavMenu;

