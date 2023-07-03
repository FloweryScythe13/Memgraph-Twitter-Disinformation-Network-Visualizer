import Container from "react-bootstrap/esm/Container";

const Home = () => {
    return <Container>
        <h1>Home</h1>
            <p>Welcome to the live demo of the Twitter Disinformation Network Visualizer web app, created with love during the international 2021-2022 Memgraph App Challenge Hackathon. </p>

            <p>This full-stack application serves as a proof-of-concept for investigating historical influence operations campaigns from Yevgeny Prigozhin's notorious Internet Research Agency and other disinformation threat actors, using graph databases and social network analysis in 3D.</p>
            <br></br>
            <p>To get started, open the Past IRA Campaigns menu in the top left corner and select the Northern Africa campaign (which targeted the Central African Republic from ~2018-2021).</p>

        </Container>
};
  
export default Home;