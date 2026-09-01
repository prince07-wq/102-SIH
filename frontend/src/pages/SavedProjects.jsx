import SavedProjectList from '../components/SavedProjectList';
import './UtilityPages.css';

export default function SavedProjects() {
  return (
    <div className="utility-page">
      <h1>Saved / Review List</h1>
      <p className="utility-page__lede">Saved in this browser only. These selections are not server-persisted.</p>
      <SavedProjectList />
    </div>
  );
}
