import { useEffect, useState } from 'react';
import api from '../../services/api';
import { useRouter } from 'next/router';

interface Job {
  id: string;
  title: string;
  status: string;
  priority: string;
  type: string;
}

export default function Dashboard() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await api.get('/api/v1/jobs');
        setJobs(res.data);
      } catch (err: any) {
        console.error(err);
        if (err.response && err.response.status === 401) {
          // Redirect to login if unauthorized
          router.push('/');
        }
        setError('Failed to fetch jobs');
      }
    };
    fetchJobs();
  }, [router]);

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Jobs</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ddd', padding: '8px' }}>Title</th>
            <th style={{ border: '1px solid #ddd', padding: '8px' }}>Status</th>
            <th style={{ border: '1px solid #ddd', padding: '8px' }}>Priority</th>
            <th style={{ border: '1px solid #ddd', padding: '8px' }}>Type</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id}>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>{job.title}</td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>{job.status}</td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>{job.priority}</td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>{job.type}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}