import LightController from "../Components/LightControl";

const Dashboard = () => {
    return (
        <>
            <LightController
                room={"bedroom"}
                lights={["light1", "light2", "light3"]}
            />
            
        </>
    );
};
export default Dashboard;
