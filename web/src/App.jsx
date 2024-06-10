import Welcome from "./components/Welcome"
import styles from './ui/home.module.css';

export default function App() {
  return (
      <>
      <Welcome />

      <div
        className="h-0 w-0 border-b-[30px] border-l-[20px] border-r-[20px] border-b-black border-l-transparent border-r-transparent"
        />

      <div className={styles.shape} />

      
      <p className="font-['Lusitana'] ">
        This is with Font Link. We are linking the fonts from the Google Fonts.
        </p>

      </>
  );

}

