import { useState } from "react"
import { useDispatch } from "react-redux"
import InputText from '../../../components/Input/InputText'
import ErrorText from '../../../components/Typography/ErrorText'
// import { showNotification } from "../../common/headerSlice"
import { addNewProject } from "../projectSlice"

const INITIAL_PROJECT_OBJ = {
    repo_url : "",
    name : "",
    repo_branch : ""
}

function AddProjectModalBody({closeModal}){
    const dispatch = useDispatch()
    const [loading, setLoading] = useState(false)
    const [errorMessage, setErrorMessage] = useState("")
    const [projectObj, setProjectObj] = useState(INITIAL_PROJECT_OBJ)


    const saveNewProj = () => {
        if(projectObj.repo_url.trim() === "") return setErrorMessage("Repo URL is required!")
        else if(projectObj.name.trim() === "") return setErrorMessage("Project Name is required!")
        else if(projectObj.repo_branch.trim() === "") return setErrorMessage("Repo branch is required!")
        else{
            let newProjectObj = {
                "id": 7,
                "repo_url": projectObj.repo_url,
                "name": projectObj.name,
                "repo_branch": projectObj.repo_branch,
            }
            dispatch(addNewProject({newProjectObj}))
            // dispatch(showNotification({message : "New Lead Added!", status : 1}))
            closeModal()
        }
    }

    const updateFormValue = ({updateType, value}) => {
        setErrorMessage("")
        setProjectObj({...projectObj, [updateType] : value})
    }

    return(
        <>

            <InputText type="text" defaultValue={projectObj.first_name} updateType="repo_url" containerStyle="mt-4" labelTitle="Repo URL" updateFormValue={updateFormValue}/>

            <InputText type="text" defaultValue={projectObj.last_name} updateType="name" containerStyle="mt-4" labelTitle="Project Name" updateFormValue={updateFormValue}/>

            <InputText type="email" defaultValue={projectObj.email} updateType="repo_branch" containerStyle="mt-4" labelTitle="Repo branch" updateFormValue={updateFormValue}/>


            <ErrorText styleClass="mt-16">{errorMessage}</ErrorText>
            <div className="modal-action">
                <button  className="btn btn-ghost" onClick={() => closeModal()}>Cancel</button>
                <button  className="btn btn-primary px-6" onClick={() => saveNewProj()}>Save</button>
            </div>
        </>
    )
}

export default AddProjectModalBody
