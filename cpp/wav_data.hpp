#ifndef WAV_DATA_HPP_
#define WAV_DATA_HPP_

/*
All resampling and interpolation is done using something
that is, or is similar to, the Smith-Gosset algorithm.

The implementation here loosely follows what is described at
https://ccrma.stanford.edu/~jos/resample/Implementation.html
*/

uint8_t GUID_rest[14] = {0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x80,
						 0x00, 0x00, 0xaa, 0x00, 0x38, 0x9b, 0x71};

const int32_t FIR_zero_passes = 13, FIR_resolution = 1<<18;
const int32_t FIR_size = FIR_zero_passes*FIR_resolution;
const float PI = 3.14159265;
const float sound_speed = 340.3;
const float inv_max_tolerance = 1e-3;

float FIR_point[FIR_size];

void FIR_initialize(){
	FIR_point[0] = 1;
	for(int32_t i=1; i<FIR_size; i++){
		FIR_point[i] = std::sin(PI*((float)i/FIR_resolution))/(PI*((float)i/FIR_resolution));
	}
	FIR_point[FIR_size-1] = 0;
}

inline float FIR_read(long double p){
	return FIR_point[std::min(FIR_size-1, std::abs((int32_t)p))];
}

class Directed_wave_data{

	public:

		bool big_endian = 0;

		std::string chunk_id = "RIFF",
					wave_format = "WAVE",
					format_chunk_id = "fmt ",
					data_chunk_id = "data",
					fact_chunk_id = "fact",
					file_name;

		/*
		   default is 32-bit IEEE float mono data at 44100 Hz.
		   Note that this class transforms the given input data
		   to this specific type.
		*/


		uint32_t chunk_size = 0,
				 format_chunk_size = 40,
				 audio_format = 0xfffe,		// WAVE_FORMAT_EXTENSIBLE
				 channel_amount = 0,		// channels defined later
				 sample_rate = 44100,		// 44100 Hz
				 byte_rate = 0,
				 block_align = 0,
				 bits_per_sample = 32,
				 extension_size = 22,
				 valid_bits = 32,
				 channel_mask = 0,
				 subformat = 3,				// IEEE
				 fact_chunk_size = 4,		// <-	useless stuff for the fact chunk. Some programs
				 total_sample_length = 0,	// <-	require a fact chunk in a WAVE_FORMAT_EXTENSIBLE
				 data_chunk_size = 0,
				 sample_size = 4,			// 32-bit (4-byte)
				 samples_per_channel = 0,
				 position_rate = 147,		// = 44100/300
				 timeline_offset = 0;

		std::vector<float> *audio_data = new std::vector<float>[18];
		std::vector<std::array<float,3> > *position_data=new std::vector<std::array<float,3> >[18];
		std::vector<float> *damper_profile = new std::vector<float>[18];

		void resample(uint32_t previous_rate){
		
			long double p_conv = (float)sample_rate/previous_rate;
			long double ip_conv = 1.0/p_conv;

			samples_per_channel = 0;
			for(int i=0; i<18; i++){
				samples_per_channel = std::max(samples_per_channel, (uint32_t)audio_data[0].size());
			}

			std::vector<float> *new_data = new std::vector<float>[18];
			int32_t new_size = (int32_t)std::ceil(p_conv*samples_per_channel);

			for(uint32_t i=0; i<18; i++){
				if((channel_mask>>i)&1){
					
					new_data[i].resize(new_size, 0.0);

					long double fpos, dpos;
					int32_t ipos, kmin, kmax;

					for(int32_t j=0; j<new_size; j++){
						
						fpos = j*ip_conv;
						ipos = (int32_t)fpos;
						dpos = fpos-ipos;
						
						kmin = std::max(0, ipos-FIR_zero_passes)-ipos;
						kmax = std::min((int32_t)samples_per_channel-1, ipos+FIR_zero_passes)-ipos;

						for(int32_t k=kmin; k<=kmax; k++){

							new_data[i][j] += audio_data[i][ipos+k]
											 *FIR_read(((long double)k-dpos)*FIR_resolution);

						}
					}
				}

			}

			samples_per_channel = new_size;
			std::swap(audio_data, new_data);
			delete[] new_data;

		}

		void listen_channel(int c0, int c1, Directed_wave_data *other){
			
			int32_t size0 = (int32_t)audio_data[c0].size();
			int32_t size1 = (int32_t)other->audio_data[c1].size();
			
			int32_t psize0 = (int32_t)position_data[c0].size();
			int32_t psize1 = (int32_t)other->position_data[c1].size();

			int32_t offset = other->timeline_offset-timeline_offset;
			
			int32_t ppos0 = offset/300-1, ppos1 = -1;
			int32_t next_pos0 = offset+((300+(offset%300))%300);
			int32_t next_pos1 = 0;
			
			if(offset%300 != 0) next_pos1 -= 300;


			float xpos0 = 0, ypos0 = 0, rpos0 = 0, diffx0 = 0, diffy0 = 0, diffr0 = 0, mid0 = 0;
			float xpos1 = 0, ypos1 = 0, diffx1 = 0, diffy1 = 0, mid1 = 0;

			const float otherpos1 = (float)((300+(offset%300))%300)/300.0;
			const float otherpos0 = 1-otherpos1;
			
			const float div300 = 1.0/300.0;

			bool position_changed = 0;

			float dire = 0, ddire = 0, damping = 1, dist = 1, ddist = 0, time = 0;
			long double wave_compress = 1;

			int32_t jipos, kmin, kmax;
			long double jfpos, jdpos;

			std::cout.setf(std::ios::fixed);
			std::cout.precision(10);
			
			for(int32_t i=0, j=offset; i<size1; i++, j++){
				
				if(i>=next_pos1){
					
					ppos1++;
					
					xpos1 = other->position_data[c1][std::min(psize1-1, ppos1)][0];
					ypos1 = other->position_data[c1][std::min(psize1-1, ppos1)][1];
					
					diffx1 = other->position_data[c1][std::min(psize1-1, ppos1+1)][0]
							-other->position_data[c1][std::min(psize1-1, ppos1)][0];
					diffy1 = other->position_data[c1][std::min(psize1-1, ppos1+1)][1]
							-other->position_data[c1][std::min(psize1-1, ppos1)][1];
				
					next_pos1 += 300;

					mid1 = 0;
					mid0 = otherpos0;

					position_changed = 1;

				}

				if(j>=next_pos0){
					
					ppos0++;
					
					xpos0  = position_data[c0][std::min(psize0-1, std::max(0, ppos0))][0];
					ypos0  = position_data[c0][std::min(psize0-1, std::max(0, ppos0))][1];
					rpos0  = position_data[c0][std::min(psize0-1, std::max(0, ppos0))][2];
					
					diffx0 = position_data[c0][std::min(psize0-1, std::max(0, ppos0+1))][0]
							-position_data[c0][std::min(psize0-1, std::max(0, ppos0))][0];
					diffy0 = position_data[c0][std::min(psize0-1, std::max(0, ppos0+1))][1]
							-position_data[c0][std::min(psize0-1, std::max(0, ppos0))][1];
					diffr0 = position_data[c0][std::min(psize0-1, std::max(0, ppos0+1))][2]
							-position_data[c0][std::min(psize0-1, std::max(0, ppos0))][2];
				

					next_pos0 += 300;

					mid0 = 0;
					mid1 = otherpos1;

					position_changed = 1;

				}

				if(position_changed){
						
					float x0 = xpos0+mid0*diffx0-xpos1-mid1*diffx1;
					float y0 = ypos0+mid0*diffy0-ypos1-mid1*diffy1;

					if(x0 == 0.0) x0 = 1e-9;

					float rot0 = std::atan(y0/x0)/PI;
					
					if(rot0*y0 < 0) rot0 += 1.0;
					if(rot0 < 0) rot0 += 2.0;
						
					float x1 = x0+diffx0-diffx1;
					float y1 = y0+diffy0-diffy1;

					if(x1 == 0.0) x1 = 1e-9;

					float rot1 = std::atan(y1/x1)/PI;
					
					if(rot1*y1 < 0) rot1 += 1.0;
					if(rot1 < 0) rot1 += 2.0;
					
					dist = std::sqrt(x0*x0+y0*y0);
					ddist = std::sqrt(x1*x1+y1*y1)-dist;

					wave_compress = (sound_speed+ddist*147)/sound_speed;

					dire = rot0-rpos0-mid0*diffr0;
					ddire = rot1-rot0-diffr0;

					time = 0;

					position_changed = 0;

				}

				damping = dist+time*ddist;
				//damping = 1/(std::max(inv_max_tolerance, damping*damping));
				damping = 1/(std::max(inv_max_tolerance, std::abs(damping)));
				//damping = 1;

				damping *= damper_profile[c0][(uint8_t)((dire+time*ddire)*(1<<7))];
				
				jfpos = (long double)j+((dist+ddist*time)/sound_speed)*sample_rate;
				jipos = (int32_t)jfpos;
				jdpos = jfpos-jipos;

				kmin = std::max(0, jipos-FIR_zero_passes)-jipos;
				kmax = std::min(size0-1, jipos+FIR_zero_passes)-jipos;

				for(int32_t k=kmin; k<=kmax; k++){

					audio_data[c0][jipos+k] += other->audio_data[c1][i]*damping
									 		  *FIR_read(
													  ((long double)k-jdpos)
													  *wave_compress*FIR_resolution
													  );

				}

				time += div300;
			}
			
		}

		void listen(Directed_wave_data *other){
			
			for(int c0=0; c0<18; c0++){
				if((channel_mask>>c0)&1){	
					for(int c1=0; c1<18; c1++){
						if((other->channel_mask>>c1)&1){
							listen_channel(c0, c1, other);
						}
					}
				}
			}

		}

		std::string write_file(){
			
			uint16_t temp1 = 0x0102;
			char *temp2 = (char *)&temp1;
			big_endian = (*temp2 == 1);
			if(big_endian) return "ERROR: SYSTEM IS BIG-ENDIAN";
			
			for(int i=0; i<18; i++){
				if((channel_mask>>i)&1){
					samples_per_channel = (uint32_t)audio_data[i].size();
					break;
				}
			}
			
			for(int i=0; i<18; i++){
				if((channel_mask>>i)&1){
					if((uint32_t)audio_data[i].size() < samples_per_channel){
						audio_data[i].resize(samples_per_channel, 0.0);
					}
				}
			}

			block_align = channel_amount*sample_size;
			byte_rate = sample_rate*block_align;

			uint64_t temp_size = samples_per_channel*block_align;
			if(temp_size+72 >= (uint64_t)1<<32) return "ERROR: FILE WOULD BE TOO LARGE";
			
			data_chunk_size = temp_size;
			chunk_size = data_chunk_size + 72;
			
			total_sample_length = data_chunk_size/(sample_size);

			std::ofstream file_out(file_name);
			
			file_out.write(chunk_id.c_str(), 4);
			file_out.write((char *)&chunk_size, 4);
			file_out.write(wave_format.c_str(), 4);

			file_out.write(format_chunk_id.c_str(), 4);
			file_out.write((char *)&format_chunk_size, 4);
			file_out.write((char *)&audio_format, 2);
			file_out.write((char *)&channel_amount, 2);
			file_out.write((char *)&sample_rate, 4);
			file_out.write((char *)&byte_rate, 4);
			file_out.write((char *)&block_align, 2);
			file_out.write((char *)&bits_per_sample, 2);
			file_out.write((char *)&extension_size, 2);
			file_out.write((char *)&valid_bits, 2);
			file_out.write((char *)&channel_mask, 4);
			file_out.write((char *)&subformat, 2);
			file_out.write((char *)GUID_rest, 14);
			
			file_out.write(fact_chunk_id.c_str(), 4);
			file_out.write((char *)&fact_chunk_size, 4);
			file_out.write((char *)&total_sample_length, 4);

			file_out.write(data_chunk_id.c_str(), 4);
			file_out.write((char *)&data_chunk_size, 4);

			uint32_t buff_size = 1<<15;
			float *buff = new float[buff_size*channel_amount];

			for(uint32_t i=0; i<samples_per_channel; i+=buff_size){
				uint32_t read_size = std::min(buff_size, samples_per_channel-i);
				for(uint32_t ch=0, j=0; ch<18; ch++){
					if((channel_mask>>ch)&1){
						for(uint32_t k=0; k<read_size; k++){
							buff[j+channel_amount*k] = audio_data[ch][i+k];
						}
					}
					j++;
				}
				file_out.write((char *)buff, read_size*channel_amount*4);
			}

			file_out.close();

			std::string message;
			message = "OK\nchunk ID: "+chunk_id
					+ "\nchunk size: "+std::to_string(chunk_size)
					+ "\nchunk format: "+wave_format
					+ "\nformat chunk ID: "+format_chunk_id
					+ "\nformat chunk size: "+std::to_string(format_chunk_size)
					+ "\naudio format: "+std::to_string(audio_format)
					+ "\nchannel amount: "+std::to_string(channel_amount)
					+ "\nsample rate: "+std::to_string(sample_rate)
					+ "\nbyte_rate: "+std::to_string(byte_rate)
					+ "\nblock align: "+std::to_string(block_align)
					+ "\nbits per sample: "+std::to_string(bits_per_sample)
					+ "\nchannel mask: "+std::bitset<16>(channel_mask).to_string()
					+ "\naudio subformat: "+std::to_string(subformat)
					+ "\ndata chunk ID: "+data_chunk_id
					+ "\ndata chunk size: "+std::to_string(data_chunk_size);
			return message;

		}

};

#endif
