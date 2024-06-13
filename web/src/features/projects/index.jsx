import { useEffect } from "react"
import { useDispatch, useSelector } from "react-redux"
import TrashIcon from '@heroicons/react/24/outline/TrashIcon'

import TitleCard from "../../components/Cards/TitleCard"
import { openModal } from "../common/modalSlice"
import { CONFIRMATION_MODAL_CLOSE_TYPES, MODAL_BODY_TYPES } from '../../utils/globalConstantUtil'
import { getProjects } from "./projectSlice"

const TopSideButtons = () => {

    const dispatch = useDispatch()

    const openAddNewLeadModal = () => {
        dispatch(openModal({title : "Create New Project", bodyType : MODAL_BODY_TYPES.PROJECT_ADD_NEW}))
    }

    return(
        <div className="inline-block float-right">
            <button className="btn px-6 btn-sm normal-case btn-primary" onClick={() => openAddNewLeadModal()}>Create Project</button>
        </div>
    )
}


function Projects() {
    const { projects } = useSelector(state => state.project)
    const dispatch = useDispatch()

    useEffect(() => {
        dispatch(getProjects())
    }, [])

    return(
        <>
            
            <TitleCard title="Current Projects" topMargin="mt-2" TopSideButtons={<TopSideButtons />}>

              {/* Leads List in table format loaded from slice after api call */}
              <div className="overflow-x-auto w-full">
                <table className="table w-full">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Branch</th>
                      <th>Updated At</th>
                      <th>Status</th>
                      <th>Assigned To</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {
                      projects.map((p, k) => {
                        return(
                          <tr key={k}>
                            <td>
                              <div className="flex items-center space-x-3">
                                <div className="avatar">
                                  <div className="mask mask-squircle w-12 h-12">
                                    {/* <img src={p.avatar} alt="Avatar" /> */}
                                  </div>
                                </div>
                                <div>
                                  <div className="font-bold">{p.name}</div>
                                  <div className="text-sm opacity-50"></div>
                                </div>
                              </div>
                            </td>
                            <td>
                              {p.branch}
                            </td>
                            <td>{p.last_commit_at}</td>
                            <td></td>
                            <td></td>
                            <td><button className="btn btn-square btn-ghost" onClick={() => {}}><TrashIcon className="w-5"/></button></td>
                          </tr>
                        )
                      })
                    }
                  </tbody>
                </table>
              </div>
            </TitleCard>
        </>
    )
  
}

export default Projects
